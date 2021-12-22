class Face:
    """
    Represents the hitbox of a face.
    """

    def __init__(self, x, y, width, height, rotation, translation):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.translation = translation

    def __repr__(self):
        return (
            f"Face({self.x}, "
            f"{self.y}, "
            f"{self.width}, "
            f"{self.height}, "
            f"{self.rotation}, "
            f"{self.translation})"
        )
