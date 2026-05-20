import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from backend.app import legacy_flask_app
    from backend.services.face_recognition_service import FaceRecognitionService

    with legacy_flask_app.app_context():
        encodings, names = FaceRecognitionService.loadKnownFacesFromDb()

        print(f"[INFO] known encodings: {len(encodings)}")
        print(f"[INFO] known names: {names}")

        if not encodings:
            raise RuntimeError("No known face encodings loaded")

        print("[OK] Known faces loaded successfully")


if __name__ == "__main__":
    main()