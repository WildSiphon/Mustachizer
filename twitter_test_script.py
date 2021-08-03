import logging
import sys

from modules.twitter.bot import BotTwitter

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

twitter = BotTwitter(debug=True)
twitter.reply_to_last_mentions()

# placer = MustachePlacer(debug=True)
# finder = FaceFinder(debug=True)

# image = Image.open("./test.jpg")
# logging.debug("Image size: %s", image.size)

# camera = Camera(image, numpy.zeros((4, 1)))

# DebugDrawer.instance().load(image)

# faces = finder.find_faces(image, camera)
# logging.debug("Found %d face(s) !", len(faces))
# logging.debug("Faces:\n%s", faces)

# placer.place_mustache(image, camera, faces[0])

# ImageShow.show(image)