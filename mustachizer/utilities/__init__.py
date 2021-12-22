import json
from pathlib import Path

from mustachizer.utilities.errors import JSONLoaderError


def LoadJSON(filepath: Path) -> dict:
    """
    Load a json file.

    :param filepath: path to a json file
    :return: loaded json file
    :raises JSONLoaderError: something wrong happened during loading
    """
    try:
        with open(filepath) as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        error = f"Could not read '{filepath}' content."
        raise JSONLoaderError(error) from None
    except IOError:
        error = f"'{filepath}' does not appear to exist."
        raise JSONLoaderError(error) from None


FORMATS_SUPPORTED = [
    "BAY",
    "BW",
    "CR2",
    "CRW",
    "DNG",
    "EMF",
    "EMZ",
    "G3F",
    "G3N",
    "GIF",
    "HDP",
    "JFIF",
    "JP2",
    "JPC",
    "JPE",
    "JPEG",
    "JPG",
    "MRW",
    "NEF",
    "NRW",
    "ORF",
    "PCC",
    "PDD",
    "PEF",
    "PNG",
    "PXM",
    "RAF",
    "RAW",
    "RLE",
    "SCR",
    "SRF",
    "TARGA",
    "WMF",
    "X3F",
    "XCF",
]
FORMATS_NOT_SUPPORTED = [
    "BMP",
    "ICB",
    "PBM",
    "PCD",
    "PCT",
    "PCX",
    "PGM",
    "PPM",
    "PSD",
    "RGB",
    "SGI",
    "TGA",
    "TIF",
    "TIFF",
    "VDA",
    "VST",
    "WEBP",
]
FORMATS_NOT_TESTED = [
    "ICO",
    "ICNS",
    "DIB",
    "WMZ",
    "EMZ",
    "J2K",
    "J2C",
    "FAX",
    "WIN",
    "RGBA",
    "DCX",
    "BPG",
]
