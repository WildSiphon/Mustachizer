from enum import Enum

import numpy

# PATH="/home/pi/Bots/Stachebot/"
PATH = "./"


class MustacheType(Enum):
    """Enumerate all the different staches from our collection."""

    BAMBINO = {
        "name": "BAMBINO",
        "image_path": f"{PATH}img/mustaches_collection/Bambino.png",
        "anchor": numpy.float32([0, -70, -50]),
        "width": 0.6,
    }
    CAPTAIN_HOOK = {
        "name": "CAPTAIN_HOOK",
        "image_path": f"{PATH}img/mustaches_collection/Captain_Hook.png",
        "anchor": numpy.float32([10, -90, -50]),
        "width": 0.8,
    }
    DOCTOR_WATSON = {
        "name": "DOCTOR_WATSON",
        "image_path": f"{PATH}img/mustaches_collection/Doctor_Watson.png",
        "anchor": numpy.float32([0, -80, -50]),
        "width": 0.6,
    }
    EDWARDIAN = {
        "name": "EDWARDIAN",
        "image_path": f"{PATH}img/mustaches_collection/Edwardian.png",
        "anchor": numpy.float32([10, -50, -50]),
        "width": 0.7,
    }
    FANCY_CURL = {
        "name": "FANCY_CURL",
        "image_path": f"{PATH}img/mustaches_collection/Fancy_Curl.png",
        "anchor": numpy.float32([0, -70, -50]),
        "width": 0.6,
    }
    HANDLEBAR = {
        "name": "HANDLEBAR",
        "image_path": f"{PATH}img/mustaches_collection/Handlebar.png",
        "anchor": numpy.float32([0, -80, -50]),
        "width": 0.7,
    }
    HERCULE_POIROT = {
        "name": "HERCULE_POIROT",
        "image_path": f"{PATH}img/mustaches_collection/Hercule_Poirot.png",
        "anchor": numpy.float32([0, -85, -50]),
        "width": 0.7,
    }
    HULK_HOGAN = {
        "name": "HULK_HOGAN",
        "image_path": f"{PATH}img/mustaches_collection/Hulk_Hogan.png",
        "anchor": numpy.float32([0, -140, -50]),
        "width": 0.6,
    }
    KAISER_WILHELM = {
        "name": "KAISER_WILHELM",
        "image_path": f"{PATH}img/mustaches_collection/Kaiser_Wilhelm.png",
        "anchor": numpy.float32([0, -65, -50]),
        "width": 0.7,
    }
    REVERSE_HANDLEBAR = {
        "name": "REVERSE_HANDLEBAR",
        "image_path": f"{PATH}img/mustaches_collection/Reverse_Handlebar.png",
        "anchor": numpy.float32([0, -95, -50]),
        "width": 0.65,
    }
    ROLLIE_FINGERS = {
        "name": "ROLLIE_FINGERS",
        "image_path": f"{PATH}img/mustaches_collection/Rollie_Fingers.png",
        "anchor": numpy.float32([0, -70, -50]),
        "width": 0.6,
    }
    SALVADOR_DALI = {
        "name": "SALVADOR_DALI",
        "image_path": f"{PATH}img/mustaches_collection/Salvador_Dali.png",
        "anchor": numpy.float32([0, -50, -50]),
        "width": 0.8,
    }
    TRYPHON_TOURNESOL = {
        "name": "TRYPHON_TOURNESOL",
        "image_path": f"{PATH}img/mustaches_collection/Tryphon_Tournesol.png",
        "anchor": numpy.float32([0, -85, -50]),
        "width": 0.8,
    }
    WRESTLER = {
        "name": "WRESTLER",
        "image_path": f"{PATH}img/mustaches_collection/Wrestler.png",
        "anchor": numpy.float32([0, -100, -50]),
        "width": 0.6,
    }

    """Pas top celles-là
    THIN_STRAIGHT = {
        "name":"THIN_STRAIGHT"
        "image_path":f"{PATH}img/mustaches_collection/Thin_Straight.png",
        "anchor":numpy.float32([0, -70, -50]),
        "width":0.7,
    }
    MAGNUM = f"{PATH}img/mustaches_collection/Magnum.png"
    """
