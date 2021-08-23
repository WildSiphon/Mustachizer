import io
import logging
import numpy
import sys
from PIL import Image
from PIL import ImageShow

from modules.mustache.mustachizer import Mustachizer
from modules.mustache.mustache_placer import MustachePlacer
from modules.mustache.face_finder import FaceFinder
from modules.mustache.debug_drawer import DebugDrawer
from modules.mustache.camera import Camera

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

debug = False

placer = MustachePlacer(debug)
finder = FaceFinder(debug)
mustachizer = Mustachizer(debug)

buffer = None

with open("./img/face.gif", "rb") as image_file:
    buffer = io.BytesIO(image_file.read())

image = mustachizer.mustachize(buffer)

with open("/tmp/face.gif", "wb") as save_file:
    save_file.write(image.read())

image = Image.open(image, formats=mustachizer.supported_formats)

ImageShow.show(image)
