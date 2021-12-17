import logging
import math

import cv2
import numpy
from PIL import Image

from mustachizer import PATH
from mustachizer.tools.camera import Camera
from mustachizer.tools.debug_drawer import DebugDrawer
from mustachizer.tools.face import Face

faceCascade = cv2.CascadeClassifier(
    f"{PATH}/models/haarcascade/frontalface_default.xml"
)


class FaceFinder:
    """
    Finds the bounding boxes of faces.
    """

    FACE_3D_POINTS = numpy.array(
        [
            (0.0, 0.0, 0.0),  # Nose tip
            (0.0, -330.0, -65.0),  # Chin
            (-225.0, 170.0, -135.0),  # Left eye corner
            (225.0, 170.0, -135.0),  # Right eye corner
            (-150.0, -150.0, -125.0),  # Left mouth
            (150.0, -150.0, -125.0),  # Right mouth
        ]
    )
    FACE_2D_INDEXES = [30, 8, 36, 45, 48, 54]

    def __init__(self, debug=False):
        self.debug = debug
        self._face_marker = cv2.face.createFacemarkLBF()
        self._face_marker.loadModel(f"{PATH}/models/face_marker_models/lbf.model")

    def _compute_face_projections(self, cv2_image, camera: Camera, faces) -> list:
        _, face_marks = self._face_marker.fit(cv2_image, faces)
        face_marks = [marks.reshape(68, 2) for marks in face_marks]

        projections = []
        for i in range(len(faces)):
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.FACE_3D_POINTS,
                face_marks[i][self.FACE_2D_INDEXES],
                camera.matrix,
                camera.distortion,
            )
            rotation_vector_degree = rotation_vector * 180 / math.pi
            logging.debug("Rotation: %s", rotation_vector_degree)
            logging.debug("Translation: %s", translation_vector)
            projections.append((rotation_vector, translation_vector))

            if self.debug:
                drawer = DebugDrawer.instance().drawer
                for j, mark in enumerate(face_marks[i]):
                    drawer.text(
                        mark, f"{j}", "blue" if j in self.FACE_2D_INDEXES else "lime"
                    )

        return projections

    def find_faces(self, image: Image, camera: Camera) -> list:
        cv2_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        cv2_gray_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            cv2_gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        if len(faces) == 0:
            return []
        projections = self._compute_face_projections(cv2_gray_image, camera, faces)

        return [
            Face(*face, *projection) for face, projection in zip(faces, projections)
        ]
