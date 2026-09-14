"""Angle and body-position math for pose landmarks. Assumes a side-view camera."""

import math

# MediaPipe Pose landmark indices
LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST = 11, 13, 15
RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST = 12, 14, 16


def _side_indices(side):
    if side == "left":
        return LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST
    return RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST


def angle_at_point(a, b, c):
    """Angle at point b (in degrees), given three landmarks with .x/.y."""
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)

    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(*ba)
    mag_bc = math.hypot(*bc)
    if mag_ba == 0 or mag_bc == 0:
        return None

    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_angle))


def elbow_angle(landmarks, side="left"):
    shoulder, elbow, wrist = _side_indices(side)
    return angle_at_point(landmarks[shoulder], landmarks[elbow], landmarks[wrist])


def best_side(landmarks):
    """Pick whichever arm has better landmark visibility (the one facing the camera)."""
    left_vis = sum(landmarks[i].visibility for i in (LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST))
    right_vis = sum(landmarks[i].visibility for i in (RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST))
    return "left" if left_vis >= right_vis else "right"


def shoulder_landmark(landmarks, side="left"):
    shoulder, _, _ = _side_indices(side)
    return landmarks[shoulder]


def upper_arm_length(landmarks, side="left"):
    shoulder, elbow, _ = _side_indices(side)
    s, e = landmarks[shoulder], landmarks[elbow]
    return math.hypot(e.x - s.x, e.y - s.y)


def elbow_shoulder_offset(landmarks, side="left"):
    """Horizontal distance from elbow to shoulder, normalized by upper-arm length.

    In a side-view camera, this rises when the elbow drifts forward/back away
    from the torso (scale-invariant to camera distance).
    """
    shoulder, elbow, _ = _side_indices(side)
    s, e = landmarks[shoulder], landmarks[elbow]
    length = upper_arm_length(landmarks, side)
    if length == 0:
        return None
    return abs(e.x - s.x) / length


def effort_fraction(landmarks, side="left"):
    """Relative moment-arm effort (0-1): how horizontal the forearm currently is.

    Peaks (~1.0) when the forearm is horizontal (biggest gravity torque on the
    weight), drops toward 0 at full extension/flexion. Normalized by forearm
    length so it doesn't depend on distance from the camera.
    """
    _, elbow, wrist = _side_indices(side)
    e, w = landmarks[elbow], landmarks[wrist]
    forearm_len = math.hypot(w.x - e.x, w.y - e.y)
    if forearm_len == 0:
        return None
    return abs(w.x - e.x) / forearm_len
