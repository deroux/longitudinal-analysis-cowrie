#!/usr/bin/python
import os, sys, argparse
import json
from pathlib import Path

from Helpers import get_files_from_path, split_data_by_events

global MAX_ROBOT_TIME, LOG_FILE_PATH

try:
    with open("config.json") as json_data_file:
        data = json.load(json_data_file)
        MAX_ROBOT_TIME = float(data["settings"]["robot_max_time"])
        LOG_FILE_PATH = data["settings"]["log_file_path"]
        TOP_N_EVENTS = data["settings"]["top_n_events"]
except Exception as e:
    # fallback if config file not found
    MAX_ROBOT_TIME = 10.0
    LOG_FILE_PATH = ''
    TOP_N_EVENTS = 5
    print(e)
    pass


class Reduce:
    """
       The Reduce object contains functionality to Reduce a mapped file according to the MapReduce programming model

       Args:
        mapped_values (list of tuples): The values of the .mapped file like ([(b'{"date":"...",...}', 1),(.., 1), ...])
    """
    def __init__(self):
        pass

    def partition_func(self, mapped_values):
        """Organize mapped values by key.        
        Args:
            mapped_values (list of tuples): The values produced by the previous map step in format ([(b'{"date":"...",...}', 1),(.., 1), ...])

        Returns:
            partitioned_data: Unsorted sequence of tuples with a key and a sequence of values.
        """
        import collections
        partitioned_data = collections.defaultdict(list)

        for key, value in mapped_values:
            partitioned_data[key].append(value)

        return partitioned_data.items()

    def reduce_func(self, item):
        """Convert partitioned data for command to a tuple containing the command and the number of occurences.
         Args:
             item (tuple): One value provided by the previous Map step in format like (b'{"date":"2021-05-01","sensor":"ubuntu-18-04-lts-honeypot-01", "src_ip":"37.120.212.4","dst_port":2222}', 1)

         Returns:
             key (str):             Log data string.
             sum(occurences) (int): Reduced number of occurences of specific command across list of our tuples.

             e.g. (b'{"date":"2021-05-01","sensor":"ubuntu-18-04-lts-honeypot-01", "src_ip":"37.120.212.4","dst_port":2222}', 1536)
         """
        key, occurences = item
        return key, sum(occurences)


def run_reduce(files, outFile, n):
    """
       Runner to perform reduce operation

       Args:
        files (list(str)):  The .mapped files to be reduced.
        outFile (str):      The file to write the reduced output to, e.g. reduced.json.
        n       (int):      Get the highest # of n events for specific cowrie event.
    """
    from Reduce import Reduce
    from Helpers import bcolors, build_json
    import io, json, psutil, orjson, operator

    name = 'cowrie.json.'

    out = open(outFile, "w")
    out.write("[\n")
    out.close()

    it = 1
    for f in files:
        fl = f
        if isinstance(fl, io.TextIOWrapper):
            fl = f.name

        with open(fl) as file:
            if file.buffer.name == outFile:
                continue

            map_responses = []

            if(isinstance(f, str)):
                name += f
            else:
                name += f.name.split('.')[2]

            data = json.load(file)

            process = psutil.Process(os.getpid())
            ram = float("{:.2f}".format(process.memory_info().rss / 1000000))  # in megabytes
            print(f"RAM usage: {ram} MB \t {psutil.virtual_memory()[2]} % occupied")

            for tup in data:
                map_responses.append((orjson.dumps(tup['log']), tup['count']))

            reducer = Reduce()
            partitioned_data = reducer.partition_func(map_responses)

            reduced_values = list(map(reducer.reduce_func, partitioned_data))
            reduced_values.sort(key=operator.itemgetter(1))
            reduced_values.reverse()

            data = split_data_by_events(reduced_values, n)
            result = build_json(data)

            with open(outFile, 'a') as f:
                json.dump(result, f, indent=2)

                if it < len(files):
                    f.write(",\n")
                    it += 1

                if len(result) > 0:
                    print(f"{bcolors.OKGREEN} reduced {file.buffer.name} to {outFile} (append) {bcolors.ENDC}")
                else:
                    print(f"{bcolors.WARNING} {outFile} contains no data... please check manually {bcolors.ENDC}")

    out = open(outFile, "a")
    out.write("\n]")
    out.close()

if __name__ == "__main__":
    # !/usr/bin/env python3
    """Main function to perform reduction on remote or local.

    Params:
        filenames (list(str)): List of filenames to be reduced in format format cowrie.json.YYYY-MM-DD.mapped ...

    Returns:
        outfile: File with reduced content / information of all mapped files.
    """
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
        files = get_files_from_path(folder_path, False, True, False)

    outfile = LOG_FILE_PATH + 'reduced.json'
    run_reduce(files, outfile, TOP_N_EVENTS)