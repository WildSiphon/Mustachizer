import logging
import math
from enum import Enum

from PIL import Image
from PIL import ImageDraw

from face import Face


class MustacheType(Enum):
    DEFAULT = "./moustache.png"


class MustachePlacer:

    PROPORTION_WIDTH = 0.42

    HEIGHT_POSITION = 0.2

    def __init__(self, debug=False):
        self.debug = debug
        self._mustaches = {}
        for mustache_type in list(MustacheType):
            self._mustaches[mustache_type] = Image.open(mustache_type.value).convert("RGBA")

    def _compute_mustache_size(self, face: Face, mustache_type=MustacheType.DEFAULT):
        mustache = self._mustaches[mustache_type]
        mustache_width, mustache_height = mustache.size
        mustache_aspect_ratio = mustache_width / mustache_height
        mustache_width = int(self.PROPORTION_WIDTH * face.width)
        mustache_height = int(mustache_width / mustache_aspect_ratio)
        return mustache_width, mustache_height

    def _compute_mustache_position(self, face: Face):
        """Computes the center position of the mustache on a given face."""
        vector_length = face.height*self.HEIGHT_POSITION
        x = face.x + face.width / 2 - math.sin(math.radians(face.roll))*vector_length
        y = face.y + face.height / 2 + math.cos(math.radians(face.roll))*vector_length
        return x, y

    def place_mustache(
        self, face_image: Image, face: Face, mustache_type=MustacheType.DEFAULT
    ):
        """Place a mustache on a face."""
        if self.debug:
            drawer = ImageDraw.Draw(face_image, mode="RGBA")
            drawer.rectangle(
                (face.x, face.y, face.x + face.width, face.y + face.height),
                outline="red",
            )
            drawer.line((face.x+face.width/2, face.y, face.x+face.width/2, face.y+face.height), "red")
            drawer.line((face.x, face.y+face.height/2, face.x+face.width, face.y+face.height/2), "red")

        mustache = self._mustaches[mustache_type].copy()
        mustache_width, mustache_height = self._compute_mustache_size(
            face, mustache_type
        )
        mustache = mustache.resize((mustache_width, mustache_height))
        mustache = mustache.rotate(-face.roll, expand=True)
        mustache_center = self._compute_mustache_position(face)
        mustache_position = (
            int(mustache_center[0] - mustache.width / 2),
            int(mustache_center[1] - mustache.height / 2),
        )
        face_image.paste(mustache, mustache_position, mask=mustache.getchannel("A"))
