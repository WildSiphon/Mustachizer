import io
import os
import random

from modules.mustache.mustache_placer import MustachePlacer
from modules.mustache.face_finder import FaceFinder
from modules.mustache.camera import Camera
from modules.mustache.debug_drawer import DebugDrawer
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
        image = Image.open(image_buffer, formats=[format_]).convert("RGBA")
        DebugDrawer.instance().load(image)

        camera = Camera(image)
        faces = self.__face_finder.find_faces(image, camera)
        for face in faces:
            current_mustache = f"./img/mustaches_collection/{random.choice(os.listdir('./img/mustaches_collection'))}"
            self.__mutache_placer.place_mustache(image, camera, face, mustache_type=current_mustache)

        output_stream = io.BytesIO()
        image = image.convert("RGB")
        image.save(output_stream, format="jpeg")
        output_stream.seek(0)
        return output_stream

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value: bool):
        self.__debug = value
