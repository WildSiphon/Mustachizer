import logging
import numpy
import sys
from PIL import Image
from PIL import ImageShow

from modules.mustache.mustache_placer import MustachePlacer
from modules.mustache.face_finder import FaceFinder
from modules.mustache.debug_drawer import DebugDrawer
from modules.mustache.camera import Camera

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

placer = MustachePlacer(debug=False)
finder = FaceFinder(debug=False)

image = Image.open("./img/test.jpg")
logging.debug("Image size: %s", image.size)

camera = Camera(image, numpy.zeros((4, 1)))

DebugDrawer.instance().load(image)

faces = finder.find_faces(image, camera)
logging.debug("Found %d face(s) !", len(faces))
logging.debug("Faces:\n%s", faces)

for face in faces:
    placer.place_mustache(image, camera, face)

ImageShow.show(image)
