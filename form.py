"""Live form checks: elbow drift and torso swing.

Both use thresholds relative to the current frame only (no stored baseline
snapshot), so there's nothing that can go stale or get stuck. The derived
values get a light dedicated smoothing pass (separate from the skeleton's
own landmark filter, which is tuned for low visual lag and lets more raw
noise through) so a strict threshold doesn't flicker on that noise.
"""

from collections import deque

from angles import elbow_shoulder_offset, shoulder_landmark, upper_arm_length
from smoothing import MovingAverage

ELBOW_DRIFT_THRESHOLD = 0.05   # elbow-shoulder offset, fraction of upper-arm length (~3 deg from vertical)
DRIFT_ALLOWED_PROGRESS = 0.85  # forward drift is only flagged before this % into the rep

SWING_WINDOW = 12               # frames (~0.4s) of shoulder position history to watch
SWING_RANGE_THRESHOLD = 0.07    # peak-to-peak shoulder movement in that window, fraction of upper-arm length

STREAK_NEEDED = 3               # consecutive frames a fault must persist before it's shown


class FormChecker:
    def __init__(self):
        self.offset_smoother = MovingAverage(window=4)
        self.shoulder_x_smoother = MovingAverage(window=4)
        self.shoulder_x_history = deque(maxlen=SWING_WINDOW)
        self.drift_streak = 0
        self.swing_streak = 0

    def check(self, landmarks, side, progress):
        """Returns a list of warning strings for the current frame."""
        warnings = []

        offset = self.offset_smoother.update(elbow_shoulder_offset(landmarks, side))
        drifting = (
            offset is not None and progress is not None
            and progress < DRIFT_ALLOWED_PROGRESS
            and offset > ELBOW_DRIFT_THRESHOLD
        )
        self.drift_streak = self.drift_streak + 1 if drifting else 0
        if self.drift_streak >= STREAK_NEEDED:
            warnings.append("Elbow drifting forward - keep it tucked in")

        scale = upper_arm_length(landmarks, side)
        shoulder_x = self.shoulder_x_smoother.update(shoulder_landmark(landmarks, side).x)
        self.shoulder_x_history.append(shoulder_x)

        swinging = False
        if scale and len(self.shoulder_x_history) == SWING_WINDOW:
            spread = max(self.shoulder_x_history) - min(self.shoulder_x_history)
            swinging = spread / scale > SWING_RANGE_THRESHOLD
        self.swing_streak = self.swing_streak + 1 if swinging else 0
        if self.swing_streak >= STREAK_NEEDED:
            warnings.append("Torso swinging - control the weight, don't use momentum")

        return warnings
