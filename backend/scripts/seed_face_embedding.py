import sys
from pathlib import Path

import face_recognition


# File nằm ở: project_root/backend/scripts/seed_face_embedding.py
# parents[2] = project_root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from backend.app import legacy_flask_app
    from backend.extensions import db
    from backend.models import FaceEmbedding, Student

    rollno = 12001
    image_path = PROJECT_ROOT / "backend" / "static" / "images" / "users" / f"{rollno}.jpg"

    print(f"[INFO] PROJECT_ROOT = {PROJECT_ROOT}")
    print(f"[INFO] Image path = {image_path}")

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with legacy_flask_app.app_context():
        student = Student.query.filter_by(rollno=rollno).first()

        if not student:
            raise RuntimeError(f"Student with rollno={rollno} not found")

        print(f"[INFO] Student found: {student.rollno} - {student.name}")
        print(f"[INFO] Loading image: {image_path}")

        image = face_recognition.load_image_file(str(image_path))
        face_locations = face_recognition.face_locations(image)

        print(f"[INFO] Detected faces: {len(face_locations)}")

        if len(face_locations) == 0:
            raise RuntimeError("No face found in image. Use a clearer front-face image.")

        if len(face_locations) > 1:
            raise RuntimeError("More than one face found. Use an image with exactly one face.")

        encodings = face_recognition.face_encodings(image, face_locations)

        if not encodings:
            raise RuntimeError("Could not generate face encoding")

        embedding_vector = encodings[0].tolist()

        old_embeddings = FaceEmbedding.query.filter_by(
            student_id=student.id,
            is_active=True,
        ).all()

        for item in old_embeddings:
            item.is_active = False

        embedding = FaceEmbedding(
            student_id=student.id,
            embedding=embedding_vector,
            source_image_path=str(image_path),
            quality_score=1.0,
            is_active=True,
        )

        db.session.add(embedding)
        db.session.commit()

        print("[OK] Face embedding created successfully")
        print(f"[OK] student_id={student.id}")
        print(f"[OK] rollno={student.rollno}")
        print(f"[OK] embedding_length={len(embedding_vector)}")


if __name__ == "__main__":
    main()