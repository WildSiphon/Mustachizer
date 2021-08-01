import cv2
import math
import numpy

from PIL import Image
from face import Face

eyeCascade = cv2.CascadeClassifier("./haarcascade/eye.xml")
faceCascade = cv2.CascadeClassifier("./haarcascade/frontalface_default.xml")


class FaceFinder:
    """Finds the bounding boxes of faces."""

    def __init__(self):
        pass

    def _find_eyes(self, image: Image, gray_image: Image):
        return eyeCascade.detectMultiScale(gray_image, minNeighbors=20)

    def _compute_face_rotation(self, left_eye, right_eye):
        return int(
            math.degrees(
                math.atan((left_eye[1] - right_eye[1]) / (left_eye[0] - right_eye[0]))
            )
        )

    def find_faces(self, image: Image):
        cv2_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        cv2_gray_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            cv2_gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        eyes = self._find_eyes(cv2_image, cv2_gray_image)
        rotations = [
            self._compute_face_rotation(eyes[i], eyes[i + 1]) for i in range(len(eyes) // 2)
        ]
        return [Face(*face, rotation) for face, rotation in zip(faces, rotations)]
