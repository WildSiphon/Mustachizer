from PIL import Image


class Mustache:

    FACE_WIDTH = 500

    def __init__(self, name, image_path, width, anchor):
        self._name = name
        self._image = Image.open(image_path).convert("RGBA")
        mustache_width, mustache_height = self.image.size
        mustache_aspect_ratio = mustache_width / mustache_height
        self._width = self.FACE_WIDTH * width
        self._height = self.width / mustache_aspect_ratio
        self._anchor = anchor

    @property
    def name(self):
        return self._name

    @property
    def image(self):
        return self._image.copy()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def anchor(self):
        return self._anchor
