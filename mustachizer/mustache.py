from pathlib import Path

from numpy import float32
from PIL import Image


class Mustache:
    """
    Representation of a mustache.
    """

    FACE_WIDTH = 500
    SIZES = [1, 1.5, 2, 2.5, 3]

    def __init__(
        self, name: str, image_path: Path, proportional_width: float, anchor: float32
    ):
        """
        Construct a mustache.

        :param name: How the mustache is called.
        :param image_path: Where the mustache is.
        :param proportional_width: Proportional size of a mustache to a face.
        :param anchor: Position of a point used to place the mustache on the face.
        """
        self.name = name
        self._image = Image.open(image_path).convert("RGBA")

        # Ratio
        mustache_width, mustache_height = self.image.size
        self._mustache_aspect_ratio = mustache_width / mustache_height
        self._proportional_width = proportional_width
        self._size = 1  # Defining this ratio as default size

        # Anchor
        self.anchor = anchor

    @property
    def width(self):
        return Mustache.FACE_WIDTH * self._proportional_width * self._size

    @property
    def height(self):
        return self.width / self._mustache_aspect_ratio

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = Mustache.SIZES[size - 1]

    @property
    def image(self):
        return self._image.copy()
