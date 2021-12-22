from pathlib import Path

from numpy import float32
from PIL import Image


class Mustache:
    """
    Representation of a mustache.
    """

    FACE_WIDTH = 500

    def __init__(self, name: str, image_path: Path, width: float, anchor: float32):
        """
        Construct a mustache.

        :param name: How the mustache is called.
        :param image_path: Where the mustache is.
        :param width: Horizontal mustache width from face width (Between 0 and 1).
        :param anchor: Position of a point used to place the mustache on the face.
        """
        self.name = name
        self._image = Image.open(image_path).convert("RGBA")

        # Ratio
        mustache_width, mustache_height = self.image.size
        mustache_aspect_ratio = mustache_width / mustache_height

        # Size
        self.width = self.FACE_WIDTH * width
        self.height = self.width / mustache_aspect_ratio
        self.anchor = anchor

    @property
    def image(self):
        return self._image.copy()
