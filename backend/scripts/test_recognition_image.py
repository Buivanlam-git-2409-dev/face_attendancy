import sys
from pathlib import Path

import face_recognition


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from backend.app import legacy_flask_app
    from backend.services.face_recognition_service import FaceRecognitionService

    test_image_path = (
        PROJECT_ROOT
        / "backend"
        / "static"
        / "images"
        / "users"
        / "12001.jpg"
    )

    if not test_image_path.exists():
        raise FileNotFoundError(f"Test image not found: {test_image_path}")

    with legacy_flask_app.app_context():
        known_encodings, known_names = FaceRecognitionService.loadKnownFacesFromDb()

        print(f"[INFO] known names: {known_names}")

        image = face_recognition.load_image_file(str(test_image_path))
        locations = face_recognition.face_locations(image)
        encodings = face_recognition.face_encodings(image, locations)

        print(f"[INFO] faces in test image: {len(encodings)}")

        if not encodings:
            raise RuntimeError("No face found in test image")

        for encoding in encodings:
            name = FaceRecognitionService.resolveFaceName(
                encoding,
                known_encodings,
                known_names,
            )

            print(f"[RESULT] recognized identity: {name}")

            if name == "Unknown":
                raise RuntimeError("Face was not recognized")

        print("[OK] Recognition test passed")


if __name__ == "__main__":
    main()