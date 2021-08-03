import numpy


class Camera:
    def __init__(self, image, distortion):
        width, height = image.size
        camera_x = width / 2
        camera_y = height / 2
        focal_x = width / 2 / numpy.tan(60 / 2 * numpy.pi / 180)
        focal_y = focal_x
        self._matrix = numpy.array(
            [[focal_x, 0, camera_x], [0, focal_y, camera_y], [0, 0, 1]]
        )
        self._distortion = distortion

    @property
    def matrix(self):
        return self._matrix

    @property
    def distortion(self):
        return self._distortion
