from pathlib import Path

import numpy as np
from PIL import Image


class Mustache:
    """
    Representation of a mustache.
    """

    FACE_WIDTH = 500

    def __init__(
        self,
        name: str,
        image_path: Path,
        proportional_width: float,
        anchor: np.float32,
        max_size: float = 1.0,
    ):
        """
        Construct a mustache.

        :param name: How the mustache is called.
        :param image_path: Where the mustache is.
        :param proportional_width: Proportional size of a mustache to a face.
        :param anchor: Position of a point used to place the mustache on the face.
        :param max_size: By how much one can multiply the initial size to the maximum.
        """
        self.name = name
        self._image = Image.open(image_path).convert("RGBA")

        # Ratio
        mustache_width, mustache_height = self.image.size
        self._mustache_aspect_ratio = mustache_width / mustache_height
        self._proportional_width = proportional_width

        # Sizes
        self._size = 1  # Defining this ratio as default size
        self.sizes_list = np.arange(1.0, max_size + 0.1, 0.1)

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
    def size(self, size: str):
        if size == "massive":
            self._size = self.sizes_list[-1]
        elif size == "big":
            self._size = self.sizes_list[(len(self.sizes_list) - 1) // 2]
        else:  # Case "realist" or wrong size keyword
            self._size = self.sizes_list[0]

    @property
    def image(self):
        return self._image.copy()
