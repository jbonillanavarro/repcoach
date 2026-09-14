# Muscle Teacher — Task List (Bicep Curl v1)

## 1. Project setup
- [ ] Set up Python environment (venv), install `mediapipe`, `opencv-python`, `numpy`
- [ ] Download/bundle the MediaPipe Pose Landmarker `.task` model file
- [ ] Basic project structure (`main.py`, `pose.py`, `angles.py`, `reps.py`)

## 2. Webcam + pose pipeline
- [ ] Open webcam feed with OpenCV
- [ ] Run MediaPipe PoseLandmarker on each frame, get landmarks live
- [ ] Draw skeleton overlay (shoulder-elbow-wrist) on the video feed
- [ ] Handle "landmark not visible / person out of frame" gracefully

## 3. Angle calculation
- [ ] Extract shoulder, elbow, wrist coordinates (pick a side or auto-detect active arm)
- [ ] Compute elbow angle via vector math (atan2/dot product)
- [ ] Smooth the angle signal (moving average / low-pass filter)
- [ ] Display live angle value on screen

## 4. Rep detection
- [ ] Define angle thresholds for "extended" (~160-180°) and "flexed" (~30-50°)
- [ ] State machine: extended → flexed → extended = one rep
- [ ] Rep counter on screen
- [ ] Handle noise/false triggers (avoid double-counting from jitter)

## 5. Form evaluation rules
- [ ] Range of motion check (full vs. partial rep)
- [ ] Shoulder stability check (flag swinging/momentum)
- [ ] Elbow position check (flag elbow drifting from torso)
- [ ] Tempo check (flag reps that are too fast)

## 6. Real-time feedback UI
- [ ] On-screen text/color cues (good rep vs. fix-needed)
- [ ] Live angle + rep count overlay
- [ ] Decide feedback style (text only vs. colored skeleton lines)

## 7. Testing/calibration
- [ ] Test with real curls at varying camera angles/distances
- [ ] Test failure cases (bad lighting, occlusion, wrong arm in frame)
- [ ] Tune thresholds based on real testing

## 8. Stretch goals (later)
- [ ] Support both arms simultaneously
- [ ] Session summary (total reps, good vs. bad form %)
- [ ] Save/replay sessions for review
- [ ] Port to web (MediaPipe Tasks for Web) for phone-camera use
