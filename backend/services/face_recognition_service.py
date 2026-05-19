import os
import time

import cv2
import face_recognition
import numpy as np

from backend.repositories.attendance_repository import AttendanceRepository
from backend.video_capture import VideoCapture


class FaceRecognitionService:
    @staticmethod
    def loadKnownFaces(imagesDir: str):
        knownFaceEncodings = []
        knownFaceNames = []
        for (_, _, filenames) in os.walk(imagesDir):
            for filename in filenames:
                if filename.lower() == "temp.jpg":
                    continue
                imagePath = os.path.join(imagesDir, filename)
                image = face_recognition.load_image_file(imagePath)
                encodings = face_recognition.face_encodings(image)
                if len(encodings) == 0:
                    continue
                knownFaceNames.append(filename[:-4])
                knownFaceEncodings.append(encodings[0])
            break
        return knownFaceEncodings, knownFaceNames

    @staticmethod
    def markAttendanceFromRecognition(knownFaceName: str, course: str, lectureNo: int, markedBy: str) -> bool:
        rollNoToken = knownFaceName.split("-")[0]
        if not rollNoToken.isdigit():
            return False

        rollNo = int(rollNoToken)
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
        imagesDir="static/images/users",
        displayWindow=True,
        maxDurationSeconds=None,
    ):
        videoCapture = VideoCapture(0)
        knownFaceEncodings, knownFaceNames = FaceRecognitionService.loadKnownFaces(imagesDir)
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
                    frame, knownFaceEncodings, knownFaceNames, course, lectureNo, markedBy
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
    def processFrame(frame, knownFaceEncodings, knownFaceNames, course: str, lectureNo: int, markedBy: str):
        faceLocations = face_recognition.face_locations(frame)
        faceEncodings = face_recognition.face_encodings(frame, faceLocations)
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
