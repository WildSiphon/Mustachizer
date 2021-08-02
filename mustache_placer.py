import logging
import cv2
import math
import numpy
from enum import Enum

from PIL import Image
from PIL import ImageDraw

from face import Face
from debug_drawer import DebugDrawer
from mustache import Mustache
from camera import Camera


class MustacheType(Enum):
    DEFAULT = "./moustache.png"


class MustachePlacer:

    PROPORTION_WIDTH = 0.6
    MUSTACHE_ANCHOR = numpy.float32([0, -50, -50])

    def __init__(self, debug=False):
        self.debug = debug
        self._mustaches = {}
        for mustache_type in list(MustacheType):
            self._mustaches[mustache_type] = Mustache(
                mustache_type.value, self.PROPORTION_WIDTH
            )

    def _compute_mustache_box(self, face: Face, mustache: Mustache):
        """Computes the theorical boudning box of the mustache."""
        bottom_left_corner = self.MUSTACHE_ANCHOR - numpy.array(
            [mustache.width / 2, mustache.height / 2, 0]
        )
        upper_left_corner = self.MUSTACHE_ANCHOR + numpy.array(
            [mustache.width / 2, -mustache.height / 2, 0]
        )
        upper_right_corner = self.MUSTACHE_ANCHOR + numpy.array(
            [mustache.width / 2, mustache.height / 2, 0]
        )
        bottom_right_corner = self.MUSTACHE_ANCHOR + numpy.array(
            [-mustache.width / 2, mustache.height / 2, 0]
        )
        return numpy.array((bottom_left_corner, upper_left_corner, upper_right_corner, bottom_right_corner))

    def place_mustache(
        self,
        face_image: Image,
        camera: Camera,
        face: Face,
        mustache_type=MustacheType.DEFAULT,
    ):
        """Place a mustache on a face."""
        if self.debug:
            drawer = DebugDrawer.instance().drawer
            drawer.rectangle(
                (face.x, face.y, face.x + face.width, face.y + face.height),
                outline="red",
            )
            drawer.line(
                (
                    face.x + face.width / 2,
                    face.y,
                    face.x + face.width / 2,
                    face.y + face.height,
                ),
                "red",
            )
            drawer.line(
                (
                    face.x,
                    face.y + face.height / 2,
                    face.x + face.width,
                    face.y + face.height / 2,
                ),
                "red",
            )

        mustache = self._mustaches[mustache_type]
        mustache_image = mustache.image

        mustache_box = self._compute_mustache_box(face, mustache)
        mustache_box_projected, _ = cv2.projectPoints(
            mustache_box,
            face.rotation,
            face.translation,
            camera.matrix,
            camera.distortion,
        )
        logging.debug("Box shape: %s", mustache_box.shape)
        mustache_box_projected = [tuple(point[0]) for point in mustache_box_projected]
        logging.debug("Project box shape: %s", mustache_box_projected)
        #perspective_matrix = cv2.getPerspectiveTransform(mustache_box[:, :2], mustache_box_projected.T)
        #print(perspective_matrix)
        if self.debug:
            mustache_projected, _ = cv2.projectPoints(
                self.MUSTACHE_ANCHOR,
                face.rotation,
                face.translation,
                camera.matrix,
                camera.distortion,
            )
            drawer.text(mustache_projected, "x", "cyan")
            drawer.polygon(mustache_box_projected, outline="cyan")

        #face_image.paste(mustache, mustache_position, mask=mustache.getchannel("A"))
