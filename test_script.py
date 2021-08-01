import logging
import sys
from PIL import Image
from PIL import ImageShow

from face import Face
from mustache_placer import MustachePlacer
from face_finder import FaceFinder

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

placer = MustachePlacer(debug=True)
finder = FaceFinder()

image = Image.open("./test.jpg")
logging.debug("Image size: %s", image.size)

faces = finder.find_faces(image)
logging.debug("Found %d face(s) !", len(faces))
logging.debug("Faces:\n%s", faces)

placer.place_mustache(image, faces[0])

ImageShow.show(image)
