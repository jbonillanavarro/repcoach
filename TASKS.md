# Muscle Teacher — Task List (Bicep Curl v1)

## 1. Project setup
- [x] Set up Python environment (venv), install `mediapipe`, `opencv-python`, `numpy`
- [x] Download/bundle the MediaPipe Pose Landmarker `.task` model file
- [x] Basic project structure (`main.py`, `pose.py`, `angles.py`, `reps.py`)

## 2. Webcam + pose pipeline
- [x] Open webcam feed with OpenCV
- [x] Run MediaPipe PoseLandmarker on each frame, get landmarks live
- [x] Draw skeleton overlay (shoulder-elbow-wrist) on the video feed
- [x] Handle "landmark not visible / person out of frame" gracefully

## 3. Angle calculation
- [x] Extract shoulder, elbow, wrist coordinates (pick a side or auto-detect active arm)
- [x] Compute elbow angle via vector math (atan2/dot product)
- [x] Smooth the angle signal (moving average / low-pass filter)
- [x] Display live angle value on screen

## 4. Rep detection
- [x] Define angle thresholds for "extended" (~160-180°) and "flexed" (~30-50°)
- [x] State machine: extended → flexed → extended = one rep
- [x] Rep counter on screen
- [x] Handle noise/false triggers (avoid double-counting from jitter)

## 5. Form evaluation rules
- [ ] Range of motion check (full vs. partial rep)
- [x] Shoulder stability check (flag swinging/momentum)
- [x] Elbow position check (flag elbow drifting from torso)
- [ ] Tempo check (flag reps that are too fast)

## 6. Real-time feedback UI
- [x] On-screen text/color cues (good rep vs. fix-needed)
- [x] Live angle + rep count overlay
- [x] Decide feedback style (text only vs. colored skeleton lines)

## 7. Testing/calibration
- [x] Test with real curls at varying camera angles/distances
- [ ] Test failure cases (bad lighting, occlusion, wrong arm in frame)
- [x] Tune thresholds based on real testing

## 8. Stretch goals (later)
- [ ] Support both arms simultaneously
- [ ] Session summary (total reps, good vs. bad form %)
- [ ] Save/replay sessions for review
- [ ] Port to web (MediaPipe Tasks for Web) for phone-camera use
