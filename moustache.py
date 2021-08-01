# /usr/bin/python3

import argparse
import logging
import numpy
import sys

import matplotlib.pyplot as plt
from PIL import Image

from modules.twitter import twitter
from mustache_placer import MustachePlacer
from face_finder import FaceFinder

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def main(source_image_path, debug):

    placer = MustachePlacer(debug)
    finder = FaceFinder()

    image = Image.open(source_image_path)
    logging.debug("Image size: %s", image.size)

    faces = finder.find_faces(image)
    logging.debug("Found %d face(s) !", len(faces))
    logging.debug("Faces:\n%s", faces)

    for face in faces:
        placer.place_mustache(image, faces[0])

    # Affichage de l'image une fois les opérations exécutées
    plt.axis("off")
    plt.imshow(numpy.array(image))
    plt.show()

    # Sauvegarde de l'image sous le nom "./image.png"
    image.save("./image.png", image)

    # Connexion au compte Twitter
    twitter.connect()
    # Publication de l'image
    twitter.postMedia("./image.png", "test 2 test 3 testament")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="python script to add a mustache to people"
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="draw rectangles and print stuffs to show how it works",
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="path to the source image (default is test.jpg)",
        default="./test.jpg",
    )
    args = parser.parse_args()
    main(args.path, args.debug)
