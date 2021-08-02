from PIL import ImageDraw


class DebugDrawer:
    """A class to draw debug shapes on an image."""

    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = DebugDrawer()
        return cls.__instance

    def __init__(self):
        self.__drawer = None

    def load(self, image):
        self.__drawer = ImageDraw.Draw(image, "RGBA")

    @property
    def drawer(self):
        return self.__drawer
