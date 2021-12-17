import argparse
import io
import json
import logging
import os
import sys

import argcomplete

from mustachizer import PATH
from mustachizer.logging import LOGGING_LEVEL_LIST
from mustachizer.logging.configuration import ConfigureLogger
from mustachizer.mustache_applicator import MustacheApplicator
from mustachizer.mustache_type import MustacheType

MUSTACHES_LIST = [m.name for m in MustacheType]
MEDIA_FORMATS = json.load(
    open(PATH / "mustachizer" / "utilities" / "formats.json", "r")
)


def print_banner():
    for line in open("assets/banner.txt", "r"):
        print(line.replace("\n", ""))


def print_mustache_list():
    print("Available mustaches are :", end="\n - ")
    print(*MUSTACHES_LIST, sep="\n - ", end="\n" * 2)


def show_media(filepath):
    try:
        if sys.platform.startswith("linux"):
            os.system(f"xdg-open {filepath}")
        elif sys.platform.startswith("win32"):
            os.system(f"powershell -c {filepath}")
        elif sys.platform.startswith("darwin"):
            os.system(f"open {filepath}")
    except Exception as e:
        print(f"Can't open the mustachized media : {e}")


def main(files, mustache_name, output_location, showing):
    mustachizer = MustacheApplicator(debug=False)

    for file in files:
        logger.info(f"\nACTIVE MEDIA: '{file}'")

        if not os.path.isfile(file):
            logger.error("Not a file.\nMustachization is ignored.")
            continue

        if file.split(".")[-1].upper() not in MEDIA_FORMATS["supported"]:
            logger.error(
                "Media not supported. Only supporting "
                f"{', '.join(MEDIA_FORMATS['supported'])}.\nMustachization is ignored."
            )
            continue

        logger.info(
            "SELECTED MUSTACHE: "
            f"{mustache_name if mustache_name else '*choosen ramdomly*'}"
        )

        buffer = None

        with open(file, "rb") as image_file:
            buffer = io.BytesIO(image_file.read())

        image = mustachizer.mustachize(image_buffer=buffer, mustache_name=mustache_name)

        if output_location == "./output/" and not os.path.isdir("./output/"):
            os.mkdir("./output/")

        output_name = (
            "/"
            + file.split("/")[-1].split(".")[0]
            + "_mustachized."
            + file.split(".")[-1]
        )
        filepath = output_location + output_name
        with open(filepath, "wb") as save_file:
            save_file.write(image.read())

        logger.info("Mustachization successfully done.")

        if showing:
            show_media(filepath=filepath)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="MUSTACHE THE WORLD!! Script to mustachize everything... or almost",
        epilog=f"supported media format: {', '.join(MEDIA_FORMATS['supported'])}",
    )
    parser.add_argument(
        metavar="FILES",
        dest="paths",
        type=str,
        nargs="*",
        help="path(s) to the file(s)",
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="mustache_name",
        type=str,
        nargs="?",
        default="random",
        help='choose mustache type (default is "random")',
        choices=MUSTACHES_LIST,
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_location",
        type=str,
        nargs="?",
        default="./output/",
        help='choose output location (default is "./output/")',
    )
    parser.add_argument(
        "-l",
        "--list",
        dest="listing",
        action="store_true",
        default=False,
        help="list all the mustaches types",
    )
    parser.add_argument(
        "-s",
        "--show",
        dest="showing",
        action="store_true",
        default=False,
        help="show the mustachized media",
    )
    parser.add_argument(
        "--log",
        type=str.upper,
        help="choose level to display execution info (default is 'INFO')",
        choices=LOGGING_LEVEL_LIST,
        default="INFO",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    print_banner()

    if args.listing:
        print_mustache_list()
    if not args.paths:
        parser.error("Please indicate at least one media to mustachize")

    # Create logger at the correct level
    ConfigureLogger(console_level=args.log)
    logger = logging.getLogger("stachlog")

    files = args.paths
    if args.mustache_name.upper() not in MUSTACHES_LIST:
        if args.mustache_name != "random":
            logger.warning(
                f'"{args.mustache_name}" is not a valid mustache. '
                "A random 'stache will be assigned"
            )
            print_mustache_list()
        mustache_name = None
    else:
        mustache_name = args.mustache_name.upper()
    if os.path.isdir(args.output_location) or args.output_location == "./output/":
        output_location = args.output_location
    else:
        logger.warning(
            f'Can\'t find directory "{args.output_location}". '
            'Mustachized media(s) will be saved in "./output/"'
        )
        output_location = "./output/"

    main(
        files=files,
        mustache_name=mustache_name,
        output_location=output_location,
        showing=args.showing,
    )
