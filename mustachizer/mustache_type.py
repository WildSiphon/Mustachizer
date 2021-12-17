from enum import Enum

import numpy

from mustachizer import PATH

PATH = PATH / "assets" / "mustaches_collection"


class MustacheType(Enum):
    """
    Enumerate all the different staches from our collection.
    """

    BAMBINO = {
        "name": "BAMBINO",
        "image_path": PATH / "Bambino.png",
        "anchor": numpy.float32([0, -70, -50]),
        "width": 0.6,
    }
    CAPTAIN_HOOK = {
        "name": "CAPTAIN_HOOK",
        "image_path": PATH / "Captain_Hook.png",
        "anchor": numpy.float32([10, -90, -50]),
        "width": 0.8,
    }
    DOCTOR_WATSON = {
        "name": "DOCTOR_WATSON",
        "image_path": PATH / "Doctor_Watson.png",
        "anchor": numpy.float32([0, -80, -50]),
        "width": 0.6,
    }
    EDWARDIAN = {
        "name": "EDWARDIAN",
        "image_path": PATH / "Edwardian.png",
        "anchor": numpy.float32([10, -50, -50]),
        "width": 0.7,
    }
    FANCY_CURL = {
        "name": "FANCY_CURL",
        "image_path": PATH / "Fancy_Curl.png",
        "anchor": numpy.float32([0, -70, -50]),
        "width": 0.6,
    }
    HANDLEBAR = {
        "name": "HANDLEBAR",
        "image_path": PATH / "Handlebar.png",
        "anchor": numpy.float32([0, -80, -50]),
        "width": 0.7,
    }
    HERCULE_POIROT = {
        "name": "HERCULE_POIROT",
        "image_path": PATH / "Hercule_Poirot.png",
        "anchor": numpy.float32([0, -85, -50]),
        "width": 0.7,
    }
    HULK_HOGAN = {
        "name": "HULK_HOGAN",
        "image_path": PATH / "Hulk_Hogan.png",
        "anchor": numpy.float32([0, -140, -50]),
        "width": 0.6,
    }
    KAISER_WILHELM = {
        "name": "KAISER_WILHELM",
        "image_path": PATH / "Kaiser_Wilhelm.png",
        "anchor": numpy.float32([0, -65, -50]),
        "width": 0.7,
    }
    REVERSE_HANDLEBAR = {
        "name": "REVERSE_HANDLEBAR",
        "image_path": PATH / "Reverse_Handlebar.png",
        "anchor": numpy.float32([0, -95, -50]),
        "width": 0.65,
    }
    ROLLIE_FINGERS = {
        "name": "ROLLIE_FINGERS",
        "image_path": PATH / "Rollie_Fingers.png",
        "anchor": numpy.float32([0, -70, -50]),
        "width": 0.6,
    }
    SALVADOR_DALI = {
        "name": "SALVADOR_DALI",
        "image_path": PATH / "Salvador_Dali.png",
        "anchor": numpy.float32([0, -50, -50]),
        "width": 0.8,
    }
    TRYPHON_TOURNESOL = {
        "name": "TRYPHON_TOURNESOL",
        "image_path": PATH / "Tryphon_Tournesol.png",
        "anchor": numpy.float32([0, -85, -50]),
        "width": 0.8,
    }
    WRESTLER = {
        "name": "WRESTLER",
        "image_path": PATH / "Wrestler.png",
        "anchor": numpy.float32([0, -100, -50]),
        "width": 0.6,
    }

    """Pas top celles-là
    THIN_STRAIGHT = {
        "name":"THIN_STRAIGHT"
        "image_path":PATH / "Thin_Straight.png",
        "anchor":numpy.float32([0, -70, -50]),
        "width":0.7,
    }
    MAGNUM = PATH / "Magnum.png"
    """
