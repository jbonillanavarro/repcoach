"""Rep counting state machine driven by elbow angle."""

EXTENDED_THRESHOLD = 160  # degrees; arm considered "down"
FLEXED_THRESHOLD = 50     # degrees; arm considered "curled up"


def progress_from_angle(angle):
    """0.0 (fully extended) to 1.0 (fully flexed), clamped."""
    if angle is None:
        return None
    span = EXTENDED_THRESHOLD - FLEXED_THRESHOLD
    frac = (EXTENDED_THRESHOLD - angle) / span
    return max(0.0, min(1.0, frac))


class RepCounter:
    def __init__(self):
        self.count = 0
        self.state = "extended"  # "extended" or "flexed"

    def update(self, angle):
        """Feed the latest smoothed elbow angle. Returns True if a rep just completed."""
        if angle is None:
            return False

        completed = False

        if self.state == "extended" and angle <= FLEXED_THRESHOLD:
            self.state = "flexed"
        elif self.state == "flexed" and angle >= EXTENDED_THRESHOLD:
            self.state = "extended"
            self.count += 1
            completed = True

        return completed
