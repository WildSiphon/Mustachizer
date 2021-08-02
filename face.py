class Face:
    """Represents the hitbox of a face."""

    def __init__(self, x, y, width, height, rotation, translation):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = rotation
        self._translation = translation

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def rotation(self):
        return self._rotation

    @property
    def translation(self):
        return self._translation

    def __repr__(self):
        return f"Face({self.x}, {self.y}, {self.width}, {self.height}, {self.rotation}, {self.translation})"
