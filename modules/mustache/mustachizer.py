import logging
import io

from modules.mustache.mustache_placer import MustachePlacer
from modules.mustache.face_finder import FaceFinder
from modules.mustache.camera import Camera
from modules.mustache.debug_drawer import DebugDrawer
from PIL import Image
from PIL import ImageSequence


class Mustachizer:
    """Apply a mustaches on images.

    :param debug: Whether it should draw debug lines, defaults to False
    :type debug: bool, optional
    """

    def __init__(self, debug=False):
        self.__debug = debug
        self.__mutache_placer = MustachePlacer(debug)
        self.__face_finder = FaceFinder(debug)

    def mustachize(self, image_buffer: io.BytesIO):
        """Place mustaches on an image.

        :param image_buffer: The buffer containing the image
        :type image_buffer: io.BytesIO

        :return: The modified image
        :rtype: io.BytesIO
        """
        image = Image.open(image_buffer, formats=["JPEG", "PNG", "GIF"])
        format_ = image.format
        logging.debug("Format : %s", format_)
        logging.debug("Frames : %s", image.n_frames)
        mustachized_frames = []
        recognized_faces = False
        mustache_type = None if image.n_frames <= 1 else self.__mutache_placer.choose_mustache()

        for image_frame in ImageSequence.Iterator(image):
            image_frame = image_frame.convert("RGBA")
            logging.debug("Frame !")
            DebugDrawer.instance().load(image_frame)

            camera = Camera(image_frame)
            faces = self.__face_finder.find_faces(image_frame, camera)
            if faces:
                recognized_faces = True
                for face in faces:
                    self.__mutache_placer.place_mustache(image_frame, camera, face, mustache_type)
            mustachized_frames.append(image_frame)

        if recognized_faces:
            output_stream = io.BytesIO()
            if format_ == "JPEG":
                mustachized_frames[0] = mustachized_frames[0].convert("RGB")
            if len(mustachized_frames) == 1:
                mustachized_frames[0].save(output_stream, format=format_.lower())
            elif len(mustachized_frames) > 1:
                mustachized_frames[0].save(
                    output_stream,
                    format="GIF",
                    save_all=True,
                    append_images=mustachized_frames[1:],
                    duration=image.duration if "duration" in dir(image) else 0.1,
                )
            output_stream.seek(0)
            return output_stream
        return -1

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value: bool):
        self.__debug = value
