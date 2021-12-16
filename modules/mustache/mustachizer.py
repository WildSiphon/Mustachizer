import io
import logging

from modules.mustache.camera import Camera
from modules.mustache.debug_drawer import DebugDrawer
from modules.mustache.errors import ImageIncorrectError
from modules.mustache.errors import NoFaceFoundError
from modules.mustache.face_finder import FaceFinder
from modules.mustache.mustache_placer import MustachePlacer

from PIL import Image
from PIL import ImageSequence


class Mustachizer:
    """Apply a mustaches on images.

    :param debug: Whether it should draw debug lines, defaults to False
    :type debug: bool, optional
    """

    def __init__(self, debug=False):
        self.__debug = debug
        self.__supported_formats = ["JPEG", "PNG", "GIF"]
        self.__mustache_placer = MustachePlacer(debug)
        self.__face_finder = FaceFinder(debug)

    def mustachize(self, image_buffer: io.BytesIO, mustache_name=None):
        """Place mustaches on an image.

        :param image_buffer: The buffer containing the image
        :type image_buffer: io.BytesIO

        :raises NoFaceFoundError: No face has been found on the image
        :raises ImageIncorrectError: The provided image is not in the correct format

        :return: The modified image
        :rtype: io.BytesIO
        """
        try:
            image = Image.open(image_buffer, formats=self.__supported_formats)
        except Exception as e:
            raise ImageIncorrectError from e
            
        format_ = image.format
        logging.debug("Format : %s", format_)
        nb_frames = 1 if not hasattr(image, "n_frames") else image.n_frames
        logging.debug("Frames : %s", nb_frames)
        mustachized_frames = []
        recognized_faces = False
        mustache_type = (
            None
            if nb_frames <= 1 and not mustache_name
            else self.__mustache_placer.choose_mustache(mustache_name)
        )

        for image_frame in ImageSequence.Iterator(image):
            image_frame = image_frame.convert("RGBA")
            DebugDrawer.instance().load(image_frame)

            camera = Camera(image_frame)
            faces = self.__face_finder.find_faces(image_frame, camera)
            if faces:
                recognized_faces = True
                for face in faces:
                    self.__mustache_placer.place_mustache(
                        image_frame, camera, face, mustache_type
                    )
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
        else:
            raise NoFaceFoundError()

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value: bool):
        self.__debug = value

    @property
    def supported_formats(self):
        return self.__supported_formats
