import numpy
from enum import Enum

class MustacheType(Enum):
    # DEFAULT = { "path":"./img/moustache.png",
    #             "anchor":numpy.float32([0, -70, -50]),
    #             "width":0.7}
    BAMBINO = { "path":"./img/mustaches_collection/Bambino.png",
                "anchor":numpy.float32([0, -70, -50]),
                "width":0.6}
    CAPTAIN_HOOK = {"path":"./img/mustaches_collection/Captain_Hook.png",
                    "anchor":numpy.float32([10, -90, -50]),
                    "width":0.8}
    DOCTOR_WATSON = {"path":"./img/mustaches_collection/Doctor_Watson.png",
                    "anchor":numpy.float32([0, -80, -50]),
                    "width":0.6}
    EDWARDIAN = {"path":"./img/mustaches_collection/Edwardian.png",
                "anchor":numpy.float32([10, -50, -50]),
                "width":0.7}
    FANCY_CURL = {"path":"./img/mustaches_collection/Fancy_Curl.png",
                "anchor":numpy.float32([0, -70, -50]),
                "width":0.6}
    HANDLEBAR = {"path":"./img/mustaches_collection/Handlebar.png",
                "anchor":numpy.float32([0, -80, -50]),
                "width":0.7}
    HERCULE_POIROT = {"path":"./img/mustaches_collection/Hercule_Poirot.png",
                    "anchor":numpy.float32([0, -85, -50]),
                    "width":0.7}
    HULK_HOGAN = {"path":"./img/mustaches_collection/Hulk_Hogan.png",
                "anchor":numpy.float32([0, -140, -50]),
                "width":0.6}
    KAISER_WILHELM = { "path":"./img/mustaches_collection/Kaiser_Wilhelm.png",
                        "anchor":numpy.float32([0, -65, -50]),
                        "width":0.7}
    REVERSE_HANDLEBAR = { "path":"./img/mustaches_collection/Reverse_Handlebar.png",
                        "anchor":numpy.float32([0, -95, -50]),
                        "width":0.65}
    ROLLIE_FINGERS = { "path":"./img/mustaches_collection/Rollie_Fingers.png",
                        "anchor":numpy.float32([0, -70, -50]),
                        "width":0.6}
    SALVADOR_DALI = { "path":"./img/mustaches_collection/Salvador_Dali.png",
                    "anchor":numpy.float32([0, -50, -50]),
                    "width":0.8}
    TRYPHON_TOURNESOL = { "path":"./img/mustaches_collection/Tryphon_Tournesol.png",
                        "anchor":numpy.float32([0, -85, -50]),
                        "width":0.8}
    WRESTLER = {"path":"./img/mustaches_collection/Wrestler.png",
                "anchor":numpy.float32([0, -100, -50]),
                "width":0.6}
    
    """Pas top celles-là
    THIN_STRAIGHT = { "path":"./img/mustaches_collection/Thin_Straight.png",
                    "anchor":numpy.float32([0, -70, -50]),
                    "width":0.7}
    MAGNUM = "./img/mustaches_collection/Magnum.png"
    """