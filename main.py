"""Live bicep curl form checker (side-view camera). Press 'q' to quit."""

import time

import cv2
import mediapipe as mp

from angles import (
    best_side, elbow_angle, effort_fraction,
    LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST,
    RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST,
)
from form import FormChecker
from pose import create_landmarker
from reps import RepCounter, progress_from_angle
from smoothing import LandmarkSmoother, MovingAverage


def side_indices(side):
    if side == "left":
        return LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST
    return RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST


def draw_arm(frame, landmarks, side, w, h):
    shoulder, elbow, wrist = side_indices(side)
    pts = {}
    for idx in (shoulder, elbow, wrist):
        lm = landmarks[idx]
        pts[idx] = (int(lm.x * w), int(lm.y * h))

    cv2.line(frame, pts[shoulder], pts[elbow], (0, 255, 0), 3)
    cv2.line(frame, pts[elbow], pts[wrist], (0, 255, 0), 3)
    for p in pts.values():
        cv2.circle(frame, p, 6, (0, 0, 255), -1)


def draw_effort_bar(frame, effort, x=20, y=110, width=200, height=20):
    effort = 0.0 if effort is None else effort
    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 0), 2)
    filled = int(width * effort)
    color = (0, int(255 * (1 - effort)), int(255 * effort))
    cv2.rectangle(frame, (x, y), (x + filled, y + height), color, -1)
    cv2.putText(frame, "Effort", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)


def draw_panel(frame, x, y, width, height, alpha=0.65):
    """Translucent white backdrop so text stays legible over any background."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + width, y + height), (255, 255, 255), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    landmarker = create_landmarker()
    landmark_smoother = LandmarkSmoother()
    smoother = MovingAverage(window=3)
    rep_counter = RepCounter()
    form_checker = FormChecker()

    start_time = time.time()

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.time() - start_time) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        angle = None
        warnings = []
        effort = None

        draw_panel(frame, 10, 10, 260, 130)

        if result.pose_landmarks:
            landmarks = landmark_smoother.update(result.pose_landmarks[0], timestamp_ms / 1000.0)
            side = best_side(landmarks)
            draw_arm(frame, landmarks, side, w, h)
            angle = elbow_angle(landmarks, side=side)
            effort = effort_fraction(landmarks, side=side)

            smoothed = smoother.update(angle)
            if smoothed is not None:
                progress = progress_from_angle(smoothed)
                rep_counter.update(smoothed)
                warnings = form_checker.check(landmarks, side, progress)

                cv2.putText(frame, f"Angle: {int(smoothed)} deg", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        else:
            smoother.update(None)
            cv2.putText(frame, "Body not detected", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(frame, f"Reps: {rep_counter.count}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        draw_effort_bar(frame, effort)

        if warnings:
            draw_panel(frame, 10, 145, 480, len(warnings) * 30 + 15)
        for i, warning in enumerate(warnings):
            cv2.putText(frame, warning, (20, 165 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Muscle Teacher - Bicep Curl", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()
