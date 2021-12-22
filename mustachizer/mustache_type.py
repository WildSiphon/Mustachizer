import random
from enum import Enum

import numpy

from mustachizer import PATH
from mustachizer.mustache import Mustache

PATH = PATH / "assets" / "mustaches_collection"


class MustacheType(Enum):
    """
    Enumerate all the different staches from our collection.
    """

    BAMBINO = Mustache(
        name="BAMBINO",
        image_path=PATH / "Bambino.png",
        anchor=numpy.float32([0, -70, -50]),
        width=0.6,
    )
    CAPTAIN_HOOK = Mustache(
        name="CAPTAIN_HOOK",
        image_path=PATH / "Captain_Hook.png",
        anchor=numpy.float32([10, -90, -50]),
        width=0.8,
    )
    DOCTOR_WATSON = Mustache(
        name="DOCTOR_WATSON",
        image_path=PATH / "Doctor_Watson.png",
        anchor=numpy.float32([0, -80, -50]),
        width=0.6,
    )
    EDWARDIAN = Mustache(
        name="EDWARDIAN",
        image_path=PATH / "Edwardian.png",
        anchor=numpy.float32([10, -50, -50]),
        width=0.7,
    )
    FANCY_CURL = Mustache(
        name="FANCY_CURL",
        image_path=PATH / "Fancy_Curl.png",
        anchor=numpy.float32([0, -70, -50]),
        width=0.6,
    )
    HANDLEBAR = Mustache(
        name="HANDLEBAR",
        image_path=PATH / "Handlebar.png",
        anchor=numpy.float32([0, -80, -50]),
        width=0.7,
    )
    HERCULE_POIROT = Mustache(
        name="HERCULE_POIROT",
        image_path=PATH / "Hercule_Poirot.png",
        anchor=numpy.float32([0, -85, -50]),
        width=0.7,
    )
    HULK_HOGAN = Mustache(
        name="HULK_HOGAN",
        image_path=PATH / "Hulk_Hogan.png",
        anchor=numpy.float32([0, -140, -50]),
        width=0.6,
    )
    KAISER_WILHELM = Mustache(
        name="KAISER_WILHELM",
        image_path=PATH / "Kaiser_Wilhelm.png",
        anchor=numpy.float32([0, -65, -50]),
        width=0.7,
    )
    REVERSE_HANDLEBAR = Mustache(
        name="REVERSE_HANDLEBAR",
        image_path=PATH / "Reverse_Handlebar.png",
        anchor=numpy.float32([0, -95, -50]),
        width=0.65,
    )
    ROLLIE_FINGERS = Mustache(
        name="ROLLIE_FINGERS",
        image_path=PATH / "Rollie_Fingers.png",
        anchor=numpy.float32([0, -70, -50]),
        width=0.6,
    )
    SALVADOR_DALI = Mustache(
        name="SALVADOR_DALI",
        image_path=PATH / "Salvador_Dali.png",
        anchor=numpy.float32([0, -50, -50]),
        width=0.8,
    )
    TRYPHON_TOURNESOL = Mustache(
        name="TRYPHON_TOURNESOL",
        image_path=PATH / "Tryphon_Tournesol.png",
        anchor=numpy.float32([0, -85, -50]),
        width=0.8,
    )
    WRESTLER = Mustache(
        name="WRESTLER",
        image_path=PATH / "Wrestler.png",
        anchor=numpy.float32([0, -100, -50]),
        width=0.6,
    )

    """Pas top celles-là
    THIN_STRAIGHT = {
        "name":"THIN_STRAIGHT"
        "image_path":PATH / "Thin_Straight.png",
        "anchor":numpy.float32([0, -70, -50]),
        "width":0.7,
    }
    MAGNUM = PATH / "Magnum.png"
    """

    @classmethod
    def get_names(cls) -> list:
        return list(cls.__members__)

    @classmethod
    def random(cls):
        return random.choice(list(MustacheType))
