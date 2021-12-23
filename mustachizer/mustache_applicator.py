import io
import logging
import random

from PIL import Image, ImageSequence

from mustachizer.errors import ImageIncorrectError, NoFaceFoundError
from mustachizer.mustache_placer import MustachePlacer
from mustachizer.mustache_type import MustacheType
from mustachizer.tools.camera import Camera
from mustachizer.tools.debug_drawer import DebugDrawer
from mustachizer.tools.face_finder import FaceFinder

logger = logging.getLogger("stachlog")


class MustacheApplicator:
    """
    Apply mustaches on medias.
    """

    def __init__(self, debug: bool = False):
        """
        Construct the applicator.

        :param debug: Whether it should draw debug lines, defaults to False
        """
        self._debug = debug
        self._supported_formats = ["JPEG", "PNG", "GIF"]
        self.mustache_placer = MustachePlacer(debug=debug)
        self.face_finder = FaceFinder(debug=debug)

    def mustachize(
        self,
        image_buffer: io.BytesIO,
        mustache_name: str = "RANDOM",
        mustache_size: str = "realist",
    ) -> io.BytesIO:
        """Place mustaches on an image.

        :param image_buffer: The buffer containing the image
        :param mustache_name: Name of the mustache
        :param mustache_size: Size of the mustache (between 1 and 5)

        :raises NoFaceFoundError: No face has been found on the image
        :raises ImageIncorrectError: The provided image is not in the correct format

        :return: The modified image
        """
        logger.info("+ Mustachization:")
        try:
            image = Image.open(image_buffer, formats=self._supported_formats)
        except Exception as exception:
            error_message = "An exception occured while loading the provided image"
            raise ImageIncorrectError(error_message) from exception

        # File format
        format_ = image.format

        # Frames contained in media (more than 1 for gif)
        nb_frames = getattr(image, "n_frames", 1)

        mustachized_frames = []
        recognized_faces = False
        mustache_list = []
        max_faces_found = 0

        # Freeze mustache_name if more than one frame
        if nb_frames > 1 and mustache_name not in MustacheType.get_names():
            mustache_name = random.choice(MustacheType.get_names())

        # Iterate media by frame
        for image_frame in ImageSequence.Iterator(image):
            image_frame = image_frame.convert("RGBA")
            DebugDrawer.instance().load(image_frame)

            camera = Camera(image_frame)
            faces = self.face_finder.find_faces(image_frame, camera)
            max_faces_found = max(max_faces_found, len(faces))

            # Faces found in frame
            if faces:
                recognized_faces = True
                # Iterate each face
                for face in faces:
                    # Get mustache
                    mustache_type = getattr(
                        MustacheType, mustache_name, MustacheType.random()
                    ).value
                    mustache_type.size = mustache_size
                    mustache_list.append(mustache_type.name)
                    # Place mustache
                    self.mustache_placer.place_mustache(
                        face_image=image_frame,
                        camera=camera,
                        face=face,
                        mustache=mustache_type,
                    )
            mustachized_frames.append(image_frame)

        if not recognized_faces:
            raise NoFaceFoundError("No face found in media.")

        # Logger
        logger.debug(f"| Format : {format_}")
        logger.debug(f"| Frames : {nb_frames}")
        logger.debug(f"| Max faces found on a single frame : {max_faces_found}")
        logger.debug(f"| Mustache(s) size: {mustache_size}")
        logger.debug(f"| Number of mustaches placed: {len(mustache_list)}")
        logger.debug(f"| Mustache(s) used: {', '.join(set(mustache_list))}")

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

        logger.info("+ Done.")
        return output_stream

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = value

    @property
    def supported_formats(self):
        return self._supported_formats
