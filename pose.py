"""Wraps MediaPipe's PoseLandmarker (Tasks API) for live webcam use."""

import mediapipe as mp

MODEL_PATH = "models/pose_landmarker_lite.task"

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def create_landmarker():
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_poses=1,
    )
    return PoseLandmarker.create_from_options(options)
