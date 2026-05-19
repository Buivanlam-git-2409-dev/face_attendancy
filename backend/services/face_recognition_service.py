import os
import time

import cv2
import face_recognition
import numpy as np

from backend.extensions import db
from backend.repositories.attendance_repository import AttendanceRepository
from backend.video_capture import VideoCapture
from backend.face_detector import load_face_detector, detect_face_locations
from backend.config import Config


class FaceRecognitionService:
    @staticmethod
    def loadKnownFacesFromDb():
        """Load face embeddings from database."""
        from backend.models import FaceEmbedding, Student
        
        knownFaceEncodings = []
        knownFaceNames = []
        
        embeddings = db.session.query(FaceEmbedding, Student).join(Student).all()
        for embedding_obj, student in embeddings:
            knownFaceEncodings.append(np.array(embedding_obj.embedding))
            knownFaceNames.append(str(student.rollno))
            
        return knownFaceEncodings, knownFaceNames

    @staticmethod
    def markAttendanceFromRecognition(knownFaceName: str, course: str, lectureNo: int, markedBy: str) -> bool:
        # Note: Rollno is now just knownFaceName (student.rollno)
        rollNo = int(knownFaceName)
        
        hasExisting = AttendanceRepository.hasAnyAttendanceForRollNo(rollNo)
        alreadyMarked = AttendanceRepository.isAlreadyMarkedForLecture(rollNo, course, lectureNo)
        if (not hasExisting) or (not alreadyMarked):
            AttendanceRepository.createAttendance(rollNo, course, lectureNo, markedBy)
            return True
        return False

    @staticmethod
    def resolveFaceName(faceEncoding, knownFaceEncodings, knownFaceNames):
        if len(knownFaceEncodings) == 0:
            return "Unknown"
        matches = face_recognition.compare_faces(knownFaceEncodings, faceEncoding)
        faceDistances = face_recognition.face_distance(knownFaceEncodings, faceEncoding)
        bestMatchIndex = int(np.argmin(faceDistances))
        if matches[bestMatchIndex]:
            return knownFaceNames[bestMatchIndex]
        return "Unknown"

    @staticmethod
    def runAttendanceLoop(
        course: str,
        lectureNo: int,
        markedBy: str,
        displayWindow=True,
        maxDurationSeconds=None,
    ):
        videoCapture = VideoCapture(0)
        knownFaceEncodings, knownFaceNames = FaceRecognitionService.loadKnownFacesFromDb()
        
        # Load YOLO detector if configured
        face_detector = load_face_detector(Config.YOLO_FACE_MODEL_PATH)
        yolo_conf = Config.YOLO_FACE_CONF

        faceLocations = []
        faceNames = []
        processThisFrame = True
        isMarkedInFrame = False
        markedCount = 0
        startTime = time.time()

        while True:
            frame = videoCapture.read()
            if processThisFrame:
                faceLocations, faceNames, isMarkedInFrame, newlyMarkedCount = FaceRecognitionService.processFrame(
                    frame, knownFaceEncodings, knownFaceNames, course, lectureNo, markedBy,
                    detector=face_detector, conf=yolo_conf
                )
                markedCount += newlyMarkedCount
            processThisFrame = not processThisFrame
            if displayWindow:
                FaceRecognitionService.drawOverlay(frame, faceLocations, faceNames, isMarkedInFrame)
                cv2.imshow("Marking attendance", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            if maxDurationSeconds is not None and (time.time() - startTime) >= maxDurationSeconds:
                break

        videoCapture.release()
        if displayWindow:
            cv2.destroyAllWindows()
        return {"markedCount": markedCount}

    @staticmethod
    def processFrame(
        frame, knownFaceEncodings, knownFaceNames, course: str, lectureNo: int, markedBy: str,
        detector=None, conf=0.50
    ):
        # Use custom detector if available, else fallback to dlib
        faceLocations = detect_face_locations(frame, detector=detector, conf=conf)
        
        # face_recognition.face_encodings expects RGB frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faceEncodings = face_recognition.face_encodings(rgb_frame, faceLocations)
        
        faceNames = []
        isMarked = False
        newlyMarkedCount = 0

        for faceEncoding in faceEncodings:
            rollName = FaceRecognitionService.resolveFaceName(faceEncoding, knownFaceEncodings, knownFaceNames)
            if rollName != "Unknown":
                if FaceRecognitionService.markAttendanceFromRecognition(rollName, course, lectureNo, markedBy):
                    isMarked = True
                    newlyMarkedCount += 1
            faceNames.append(rollName)
        return faceLocations, faceNames, isMarked, newlyMarkedCount

    @staticmethod
    def drawOverlay(frame, faceLocations, faceNames, isMarked: bool):
        for (top, right, bottom, left), rollName in zip(faceLocations, faceNames):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, rollName, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
            if isMarked:
                cv2.putText(frame, "Marked", (left + 12, bottom - 12), font, 0.5, (255, 255, 255), 1)
