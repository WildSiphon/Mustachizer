import io
import os
import argparse
from modules.mustache.mustachizer import Mustachizer
from modules.mustache.mustache_type import MustacheType

def main(files,mustache_name,output_location):
    mustachizer = Mustachizer(debug=False)

    for file in files:
        print(f"\nACTIVE MEDIA: {file}")
        if not os.path.isfile(file):
            print("Not a file.\nMustachization is ignored.")
            continue
        if file.split('.')[-1].upper() not in mustachizer.supported_formats:
            print(f"Media not supported. Only supporting {', '.join(mustachizer.supported_formats)}.")
            print("Mustachization is ignored.")
            continue
        print(f"SELECTED MUSTACHE: {mustache_name}")

        buffer = None

        with open(file, "rb") as image_file:
            buffer = io.BytesIO(image_file.read())

        image = mustachizer.mustachize(image_buffer=buffer,mustache_name=mustache_name)

        if output_location == "./output/" and not os.path.isdir("./output/"):
            os.mkdir("./output/")
        
        output_name = '/'+file.split('/')[-1].split('.')[0]+'_mustachized.'+file.split('.')[-1]
        with open( output_location+output_name, "wb") as save_file:
            save_file.write(image.read())
        
        print("Mustachization successfully done.")

def printMustacheList():
    print('Available mustaches are :')
    print(*[' - '+m.name for m in MustacheType],sep='\n')

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description="MUSTACHE THE WORLD!! Script to mustachize everything... or almost",
        epilog=f"supported media format: .png .jpeg .gif"
    )
    parser.add_argument(
        metavar="PATHS",
        dest="files",
        type=str,
        nargs="*",
        help="path(s) to the file(s)",
    )
    parser.add_argument(
        "-t",
        dest="mustache_name",
        type=str,
        nargs="?",
        default="random",
        help="choose mustache type (default is \"random\")",
    )
    parser.add_argument(
        "-o",
        dest="output_location",
        type=str,
        nargs="?",
        default="./output/",
        help="choose output location (default is \"./output/\")",
    )
    parser.add_argument(
        "-l",
        dest="listing",
        action="store_true",
        default=False,
        help="list all the mustaches types",
    )
    args = parser.parse_args()
    
    if args.listing: printMustacheList()
    if args.files:
        files = args.files
        if args.mustache_name.upper() not in [m.name for m in MustacheType]:
            if args.mustache_name != "random":
                print(f"\"{args.mustache_name}\" is not a valid mustache. A random \'stache will be assigned")
                printMustacheList()
            mustache_name = None
        else:
            mustache_name = args.mustache_name.upper()
        if os.path.isdir(args.output_location) \
        or args.output_location == "./output/":
            output_location = args.output_location
        else:
            print(f"Can\'t find directory \"{args.output_location}\". Mustachized media(s) will be saved in \"./output/\"")
            output_location = "./output/"
    else:
        exit('Please indicate at least one media to mustachize\nmain.py [-h] for more informations')

    main(
        files=files,
        mustache_name=mustache_name,
        output_location=output_location
    )