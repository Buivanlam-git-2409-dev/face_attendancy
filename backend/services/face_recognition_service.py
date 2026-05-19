import time
from typing import List, Optional, Tuple

import cv2
import face_recognition
import numpy as np

from backend.config import Config
from backend.extensions import db
from backend.face_detector import detect_face_locations, load_face_detector
from backend.repositories.attendance_repository import AttendanceRepository
from backend.video_capture import VideoCapture


class FaceRecognitionService:
    @staticmethod
    def load_known_faces_from_db() -> Tuple[List[np.ndarray], List[str]]:
        """
        Load active face embeddings from database.

        Returns:
            known_face_encodings: list of numpy arrays
            known_face_names: list of student roll numbers as string
        """
        from backend.models import FaceEmbedding, Student

        known_face_encodings = []
        known_face_names = []

        embeddings = (
            db.session.query(FaceEmbedding, Student)
            .join(Student)
            .filter(FaceEmbedding.is_active.is_(True))
            .all()
        )

        for embedding_obj, student in embeddings:
            if not embedding_obj.embedding:
                continue

            known_face_encodings.append(np.array(embedding_obj.embedding))
            known_face_names.append(str(student.rollno))

        return known_face_encodings, known_face_names

    @staticmethod
    def mark_attendance_from_recognition(
        known_face_name: str,
        course: str,
        lecture_no: int,
        marked_by: str,
    ) -> bool:
        """
        Mark attendance after a recognized face is resolved to a student roll number.

        Returns:
            True if a new attendance record was created.
            False if it was already marked or invalid.
        """
        try:
            roll_no = int(known_face_name)
        except (ValueError, TypeError):
            return False

        already_marked = AttendanceRepository.isAlreadyMarkedForLecture(
            roll_no,
            course,
            lecture_no,
        )

        if already_marked:
            return False

        AttendanceRepository.createAttendance(
            roll_no,
            course,
            lecture_no,
            marked_by,
        )
        return True

    @staticmethod
    def resolve_face_name(
        face_encoding,
        known_face_encodings,
        known_face_names,
        tolerance: float = 0.5,
    ) -> str:
        """
        Resolve a face encoding to a known student roll number.

        Lower tolerance is stricter. 0.5 is safer than the default 0.6 for attendance.
        """
        if not known_face_encodings:
            return "Unknown"

        face_distances = face_recognition.face_distance(
            known_face_encodings,
            face_encoding,
        )

        if len(face_distances) == 0:
            return "Unknown"

        best_match_index = int(np.argmin(face_distances))
        best_distance = face_distances[best_match_index]

        if best_distance <= tolerance:
            return known_face_names[best_match_index]

        return "Unknown"

    @staticmethod
    def run_attendance_loop(
        course: str,
        lecture_no: int,
        marked_by: str,
        display_window: bool = True,
        max_duration_seconds: Optional[int] = None,
    ):
        """
        Legacy webcam attendance loop.

        This flow opens a local camera on the backend machine.
        For web frontend camera, prefer POST /recognition/verify.
        """
        video_capture = VideoCapture(0)
        known_face_encodings, known_face_names = (
            FaceRecognitionService.load_known_faces_from_db()
        )

        face_detector = load_face_detector(Config.YOLO_FACE_MODEL_PATH)
        yolo_conf = Config.YOLO_FACE_CONF

        face_locations = []
        face_names = []
        process_this_frame = True
        is_marked_in_frame = False
        marked_count = 0
        start_time = time.time()

        try:
            while True:
                frame = video_capture.read()

                if frame is None:
                    continue

                if process_this_frame:
                    (
                        face_locations,
                        face_names,
                        is_marked_in_frame,
                        newly_marked_count,
                    ) = FaceRecognitionService.process_frame(
                        frame,
                        known_face_encodings,
                        known_face_names,
                        course,
                        lecture_no,
                        marked_by,
                        detector=face_detector,
                        conf=yolo_conf,
                    )
                    marked_count += newly_marked_count

                process_this_frame = not process_this_frame

                if display_window:
                    FaceRecognitionService.draw_overlay(
                        frame,
                        face_locations,
                        face_names,
                        is_marked_in_frame,
                    )
                    cv2.imshow("Marking attendance", frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

                if (
                    max_duration_seconds is not None
                    and (time.time() - start_time) >= max_duration_seconds
                ):
                    break

        finally:
            video_capture.release()

            if display_window:
                cv2.destroyAllWindows()

        return {"markedCount": marked_count}

    @staticmethod
    def process_frame(
        frame,
        known_face_encodings,
        known_face_names,
        course: str,
        lecture_no: int,
        marked_by: str,
        detector=None,
        conf: float = 0.50,
    ):
        if frame is None:
            return [], [], False, 0

        face_locations = detect_face_locations(frame, detector=detector, conf=conf)

        if not face_locations:
            return [], [], False, 0

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations,
        )

        face_names = []
        is_marked = False
        newly_marked_count = 0

        for face_encoding in face_encodings:
            roll_name = FaceRecognitionService.resolve_face_name(
                face_encoding,
                known_face_encodings,
                known_face_names,
            )

            if roll_name != "Unknown":
                was_marked = FaceRecognitionService.mark_attendance_from_recognition(
                    roll_name,
                    course,
                    lecture_no,
                    marked_by,
                )

                if was_marked:
                    is_marked = True
                    newly_marked_count += 1

            face_names.append(roll_name)

        return face_locations, face_names, is_marked, newly_marked_count

    @staticmethod
    def draw_overlay(frame, face_locations, face_names, is_marked: bool):
        for (top, right, bottom, left), roll_name in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(
                frame,
                roll_name,
                (left + 6, bottom - 6),
                font,
                0.5,
                (255, 255, 255),
                1,
            )

            if is_marked:
                cv2.putText(
                    frame,
                    "Marked",
                    (left + 12, bottom - 12),
                    font,
                    0.5,
                    (255, 255, 255),
                    1,
                )

    # Backward compatibility aliases
    loadKnownFacesFromDb = load_known_faces_from_db
    markAttendanceFromRecognition = mark_attendance_from_recognition
    resolveFaceName = resolve_face_name
    runAttendanceLoop = run_attendance_loop
    processFrame = process_frame
    drawOverlay = draw_overlay