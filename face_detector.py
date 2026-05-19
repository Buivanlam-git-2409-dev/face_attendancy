import os
import cv2
import face_recognition

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


def load_face_detector(model_path='face_model/best.pt'):
    """Load a self-trained YOLO face detector.

    Returns None when the model file or ultralytics is not available, so the app
    can still start and show a clear warning/fallback behavior.
    """
    if YOLO is None:
        print('[WARN] ultralytics is not installed. Run: pip install ultralytics')
        return None

    if not os.path.isfile(model_path):
        print(f'[WARN] YOLO face model not found: {model_path}')
        print('[WARN] Train your model first, then copy best.pt to face_model/best.pt')
        return None

    print(f'[INFO] Loading YOLO face detector: {model_path}')
    return YOLO(model_path)


def _clip_box(x1, y1, x2, y2, width, height):
    x1 = max(0, min(int(x1), width - 1))
    y1 = max(0, min(int(y1), height - 1))
    x2 = max(0, min(int(x2), width - 1))
    y2 = max(0, min(int(y2), height - 1))
    return x1, y1, x2, y2


def detect_face_locations(frame, detector=None, conf=0.50):
    """Return face locations in face_recognition format: (top, right, bottom, left).

    If detector is a trained YOLO model, YOLO performs detection.
    If detector is None, this falls back to face_recognition.face_locations so
    the app remains runnable while you are still preparing/training the model.
    """
    if detector is None:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return face_recognition.face_locations(rgb_frame)

    height, width = frame.shape[:2]
    results = detector(frame, conf=conf, verbose=False)
    face_locations = []

    for result in results:
        if result.boxes is None:
            continue

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = _clip_box(x1, y1, x2, y2, width, height)

            # Convert YOLO xyxy to face_recognition location format.
            top = y1
            right = x2
            bottom = y2
            left = x1
            face_locations.append((top, right, bottom, left))

    return face_locations
