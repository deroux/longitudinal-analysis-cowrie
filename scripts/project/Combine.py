import argparse
import sys
import argparse
import io
import json

from Helpers import bcolors, write_to_file

files = []
combined = []

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # use provided files to combine
        parser = argparse.ArgumentParser()
        parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
        args = parser.parse_args()
        files = args.file

    outFile = 'reduced.json'

    for f in files:
        fl = f
        if isinstance(fl, io.TextIOWrapper):
            fl = f.name

        with open(fl) as file:
            if file.buffer.name == outFile:
                continue
            data = json.load(file)

            for element in data:
                combined.append(element)

    result = sorted(combined, key=lambda k: k['date'], reverse=False)
    write_to_file(outFile, result, 'w')