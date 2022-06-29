import argparse
import io
import logging
import os
import sys
from pathlib import Path

from mustachizer import PATH
from mustachizer.errors import ImageIncorrectError, NoFaceFoundError
from mustachizer.logging import LOGGING_LEVEL_LIST, ConfigureLogger
from mustachizer.mustache_applicator import MustacheApplicator
from mustachizer.mustache_type import MustacheType
from mustachizer.utilities import FORMATS_SUPPORTED

MUSTACHES_LIST = MustacheType.get_names()


def show_media(filepath):
    logger.info("Show the mustache(s)")
    try:
        if sys.platform.startswith("linux"):
            os.system(f"xdg-open {filepath}")
        elif sys.platform.startswith("win32"):
            os.system(f"powershell -c {filepath}")
        elif sys.platform.startswith("darwin"):
            os.system(f"open {filepath}")
    except Exception as error:
        logger.error(f"{error}")


def main(
    files: list,
    output_location: Path,
    mustache_name: str = "RANDOM",
    mustache_size: str = "realist",
    showing: bool = False,
):
    mustachizer = MustacheApplicator(debug=False)

    logger.info("Mustachizer start")

    for file in files:
        file = Path(file).resolve()

        logger.info(f"Processing file {file}")

        if not file.is_file():
            logger.error("File not found")
            continue

        if file.suffix.replace(".", "").upper() not in FORMATS_SUPPORTED:
            logger.error(f"Extension '{file.suffix}' is not supported")
            continue

        # Load file
        logger.info("Load media")
        buffer = None
        with open(file, "rb") as image_file:
            buffer = io.BytesIO(image_file.read())

        # Put mustaches on file
        try:
            image = mustachizer.mustachize(
                image_buffer=buffer,
                mustache_name=mustache_name,
                mustache_size=mustache_size,
            )
        except NoFaceFoundError as error:
            logger.error(f"{error}")
            continue
        except ImageIncorrectError as error:
            logger.error(f"{error}")
            continue

        # Create output directory if it doesn't exist yet
        output_location.mkdir(parents=True, exist_ok=True)

        # Save file
        filepath = output_location / f"{file.stem}_mustachized{file.suffix}"
        logger.info(f"New media saved {filepath}")
        with open(filepath, "wb") as save_file:
            save_file.write(image.read())

        # Display mustachize file
        if showing:
            show_media(filepath=filepath)
    else:
        logger.info("Mustachizer stop")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="MUSTACHE THE WORLD!! Script to mustachize everything... or almost",
        epilog=f"Mustaches names: {', '.join(MUSTACHES_LIST)}",
    )
    parser.add_argument(
        metavar="FILES",
        dest="paths",
        type=str,
        nargs="*",
        help="path(s) to the file(s)",
    )
    # ~~~~~~~~~~~~~ MUSTACHES RELATED SETTINGS ~~~~~~~~~~~~#
    stach = parser.add_argument_group(
        "Mustaches parameters",
        description="",
    )
    stach.add_argument(
        "--list-mustaches",
        dest="list_mustaches",
        action="store_true",
        default=False,
        help="list all the mustaches types",
    )
    stach.add_argument(
        "--size",
        type=str,
        dest="size",
        required=False,
        choices=["realist", "big", "massive"],
        default="realist",
        help='choose size of the mustache (default is "realist")',
    )
    stach.add_argument(
        "--type",
        metavar="NAME",
        dest="mustache_name",
        type=str.upper,
        nargs="?",
        default="RANDOM",
        help='choose mustache type (default is "RANDOM")',
    )
    # ~~~~~~~~~~~~~~~~~ SCRIPT'S SETTINGS ~~~~~~~~~~~~~~~~~#
    settings = parser.add_argument_group(
        "Settings",
        description="",
    )
    settings.add_argument(
        "--show",
        dest="showing",
        action="store_true",
        default=False,
        help="display the mustachized media(s)",
    )
    settings.add_argument(
        "--list-formats",
        dest="list_formats",
        action="store_true",
        default=False,
        help="list all the accepted media formats",
    )
    settings.add_argument(
        "--no-banner",
        dest="nobanner",
        required=False,
        default=False,
        action="store_true",
        help="doesn't display banner",
    )
    settings.add_argument(
        "--output",
        dest="dirpath",
        type=Path,
        nargs="?",
        default=PATH / "output",
        help='choose output location (default is "output/")',
    )
    settings.add_argument(
        "--log",
        type=str.upper,
        help='choose logging level (default is "INFO")',
        choices=LOGGING_LEVEL_LIST,
        default="INFO",
    )

    args = parser.parse_args()

    if not args.nobanner:
        print(open("assets/banner.txt", "r").read())

    if args.list_formats:
        print(
            f"\nSupported media format: {', '.join(FORMATS_SUPPORTED['supported'])}\n"
        )

    if args.list_mustaches:
        print("Available mustaches are :", end="\n - ")
        print(*MUSTACHES_LIST, sep="\n - ", end="\n" * 2)

    if not args.paths:
        parser.error("Please indicate at least one media to mustachize.")

    # Create logger at the correct level
    ConfigureLogger(console_level=args.log)
    logger = logging.getLogger("stachlog")

    files = args.paths

    # Define mustache
    mustache_name = args.mustache_name
    if mustache_name not in [*MUSTACHES_LIST, "RANDOM"]:
        logger.warning(
            f'"{mustache_name}" is not a valid mustache. '
            "A random 'stache will be assigned"
        )
        mustache_name = "RANDOM"

    # Define output directory
    output_location = args.dirpath
    if output_location.exists() and not output_location.is_dir():
        logger.warning(
            f"'{output_location}' is not a directory. "
            f"Mustachized media(s) will be saved in '{PATH}/output'"
        )
        output_location = PATH / "output"

    main(
        files=files,
        mustache_name=mustache_name,
        mustache_size=args.size,
        output_location=output_location.resolve(),
        showing=args.showing,
    )
