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
