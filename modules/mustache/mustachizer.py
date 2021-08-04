import io

from modules.mustache.mustache_placer import MustachePlacer
from modules.mustache.face_finder import FaceFinder
from modules.mustache.camera import Camera
from PIL import Image


class Mustachizer:
    """Apply a mustaches on images.

    :param debug: Whether it should draw debug lines, defaults to False
    :type debug: bool, optional
    """

    def __init__(self, debug=False):
        self.__debug = debug
        self.__mutache_placer = MustachePlacer(debug)
        self.__face_finder = FaceFinder(debug)

    def mustachize(self, image_buffer: io.BytesIO, format_=None):
        """Place mustaches on an image.

        :param image_buffer: The buffer containing the image
        :type image_buffer: io.BytesIO

        :param format_: The format of the image, default to None
        :type format_: str, optional

        :return: The modified image
        :rtype: io.BytesIO
        """
        image = Image.open(image_buffer, format_)

        camera = Camera(image)
        faces = self.__face_finder.find_faces(image, camera)
        for face in faces:
            self.__mutache_placer.place_mustache(image, camera, face)

        output_stream = io.BytesIO()
        image.save(output_stream, format="jpg")
        output_stream.seek(0)
        return output_stream

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value: bool):
        self.__debug = value
