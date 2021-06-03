#!/usr/bin/python
import argparse
import collections
import io
import operator

import ijson as ijson
import orjson, json  # as json is more conventient for writing to file
from pathlib import Path
import os, sys

from Helpers import json_help, bcolors, build_json

global MAX_ROBOT_TIME, LOG_FILE_PATH

try:
    with open("config.json") as json_data_file:
        data = json.load(json_data_file)
        MAX_ROBOT_TIME = float(data["settings"]["robot_max_time"])
        LOG_FILE_PATH = data["settings"]["log_file_path"]
except :
    # fallback if config file not found
    MAX_ROBOT_TIME = 10.0
    LOG_FILE_PATH = './'
    pass


class Reduce:
    def __init__(self):
        pass

    def partition_func(self, mapped_values):
        """Organize mapped values by their key.
        Returns an unsorted sequence of tuples with a key and a sequence of values.
        """
        partitioned_data = collections.defaultdict(list)

        for key, value in mapped_values:
            partitioned_data[key].append(value)

        return partitioned_data.items()

    def reduce_func(self, item):
        """Convert the partitioned data for a command to a
        tuple containing the word and the number of occurances.
        """
        key, occurences = item
        return key, sum(occurences)


if __name__ == "__main__":
    # necessary for remote execution
    if os.getcwd() == "/root": # we check if current directory is /root so we know we are on a digitalocean node
        LOG_FILE_PATH = "/home/cowrie/cowrie/var/log/cowrie/"

    files = []
    if len(sys.argv) > 1:
        # use provided files to reduce
        parser = argparse.ArgumentParser()
        parser.add_argument('file', type=argparse.FileType('r'), nargs='+')
        args = parser.parse_args()

        files = args.file
    else:
        # use all files in LOG_FILE_PATH
        folder_path = Path(LOG_FILE_PATH)
        for file_path in folder_path.glob('**/*.json.*'):
            filename = os.path.basename(file_path)
            if '.mapped' in filename: # or '.reduced' in filename:
                files.append(file_path)
            continue

    name = 'cowrie.json.'
    map_responses = []
    for f in files:
        fl = f
        if isinstance(fl, io.TextIOWrapper):
            fl = f.name
        with open(fl) as file:
            name += f.name.split('.')[2]
            # in_file = open(fl, 'r')
            # data = ijson.items(in_file, 'item')
            data = json.load(file)
            for tup in data:
                map_responses.append((orjson.dumps(tup['log']), tup['count']))

    reducer = Reduce()
    partitioned_data = reducer.partition_func(map_responses)

    reduced_values = []
    reduced_values = list(map(reducer.reduce_func, partitioned_data))
    reduced_values.sort(key=operator.itemgetter(1))
    reduced_values.reverse()

    helper = json_help()
    data = helper.split_data_by_events(reduced_values)
    result = build_json(data)

    outFile = LOG_FILE_PATH + '/' + name + '.reduced'

    with open(outFile, 'w') as f:
        json.dump(result, f, indent=2)

        if len(result) > 0:
            print(f"{bcolors.OKGREEN} Reduce operation finished successfully {bcolors.ENDC}")
        else:
            print(result)
            print(f"{bcolors.WARNING} Reduce operation produced no data, please check manually {bcolors.ENDC}")
