import random

import cv2
import numpy
from PIL import Image

from mustachizer.mustache import Mustache
from mustachizer.mustache_type import MustacheType
from mustachizer.tools.camera import Camera
from mustachizer.tools.debug_drawer import DebugDrawer
from mustachizer.tools.face import Face


class MustachePlacer:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self._mustaches = {}
        for mustache_type in list(MustacheType):
            self._mustaches[mustache_type] = Mustache(**mustache_type.value)

    def _compute_mustache_box(self, mustache: Mustache):
        """
        Computes the theorical boudning box of the mustache.
        """
        bottom_left_corner = mustache.anchor - numpy.array(
            [mustache.width / 2, mustache.height / 2, 0]
        )
        upper_left_corner = mustache.anchor + numpy.array(
            [mustache.width / 2, -mustache.height / 2, 0]
        )
        upper_right_corner = mustache.anchor + numpy.array(
            [mustache.width / 2, mustache.height / 2, 0]
        )
        bottom_right_corner = mustache.anchor + numpy.array(
            [-mustache.width / 2, mustache.height / 2, 0]
        )
        return numpy.array(
            (
                bottom_left_corner,
                upper_left_corner,
                upper_right_corner,
                bottom_right_corner,
            )
        )

    def choose_mustache(self, mustache_name=None):
        if mustache_name:
            mustache_type = [m for m in list(MustacheType) if m.name == mustache_name][
                0
            ]
        else:
            mustache_type = random.choice(list(MustacheType))
        return mustache_type

    def place_mustache(
        self, face_image: Image, camera: Camera, face: Face, mustache_type=None
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

        if not mustache_type:
            mustache_type = self.choose_mustache()

        mustache = self._mustaches[mustache_type]
        mustache_image = mustache.image

        mustache_box = self._compute_mustache_box(mustache)
        mustache_box_projected, _ = cv2.projectPoints(
            mustache_box,
            face.rotation,
            face.translation,
            camera.matrix,
            camera.distortion,
        )
        mustache_box_projected = [tuple(point[0]) for point in mustache_box_projected]

        mustache_box = [tuple(point[:2]) for point in mustache_box]
        original_box = numpy.float32(
            [
                [0, 0],
                [mustache_image.width, 0],
                [mustache_image.width, mustache_image.height],
                [0, mustache_image.height],
            ]
        )
        perspective_matrix = cv2.getPerspectiveTransform(
            original_box, numpy.float32(mustache_box_projected)
        )
        mustache_image = mustache_image.transpose(Image.FLIP_TOP_BOTTOM)
        cv2_image = numpy.array(mustache_image)
        cv2_image = cv2.warpPerspective(cv2_image, perspective_matrix, face_image.size)
        mustache_image = Image.fromarray(cv2_image, "RGBA")
        face_image.paste(mustache_image, (0, 0), mustache_image.getchannel("A"))

        if self.debug:
            drawer = DebugDrawer.instance().drawer
            mustache_projected, _ = cv2.projectPoints(
                mustache.anchor,
                face.rotation,
                face.translation,
                camera.matrix,
                camera.distortion,
            )
            drawer.text(mustache_projected, "x", "cyan")
            drawer.polygon(mustache_box_projected, outline="cyan")