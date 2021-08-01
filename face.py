class Face:
    """Represents the hitbox of a face."""

    def __init__(self, x, y, width, height, roll):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._roll = roll

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
    def roll(self):
        return self._roll

    @property
    def box(self):
        return (self.x, self.y+self.height, self.x+self.width, self.y)

    def __repr__(self):
        return f"Face({self.x}, {self.y}, {self.width}, {self.height}, {self.roll})"
