#!/usr/bin/python3
import json
import time
from pathlib import Path

from MapReduce import MapReduce
from Helpers import cEvent, bcolors, build_json, write_to_file
from Map import Map
from Reduce import Reduce
from Helpers import json_help

try:
    import config as cfg

    LOG_FILE_PATH = cfg.settings['log_file_path']
except ImportError:
    LOG_FILE_PATH = './'

# everything done in one map function to reduce file read overhead (open each file only once)

# [done] passwords - user:password combinations
# [done] commands - top n commands
# [done] pre_disconnect_commands - top n pre_disconnect commands
# [done] https://pypi.org/project/orjson/ replace with json
# [done] top connection attempts cowrie.session.connect src_ip
# [done] File operations
# [done] split into map  d.py and reduce.py and call from this main program
# [done] proxying requests cowrie.direct-tcpip.request
# [done] Extract Toxic HOSTS from file_download URLs

# TODO https://click.palletsprojects.com/en/8.0.x/

# TODO
# Analyze Commands for USERS / HOSTNAMES localhost etc.
# Users in Commands over Time
# Server names over Time
# look up country of src_ip in frontend
# detect whether VPN

# cowrie.client.fingerprint # If the attacker attemps to log in with an SSH public key this is logged here
# top cowrie.client.size

# cowrie.client.version
# data attempted to be sent through cowrie.direct-tcpip.data


"""
MAP
{ honeypot: "honeypotA",
  date: "2021-04-25",
  passwords: [ {user: "foo", password: "bar", count: 7}, ... /* top N attempts für den Tag */ ]}
"""


def run_map_reduce(files, mapper):
    # main work
    counts = mapper(files)
    counts.sort(key=operator.itemgetter(1))
    counts.reverse()

    helper = json_help()
    data = helper.split_data_by_events(counts)
    result = build_json(data)
    return result


"""
REDUCE
[ {date: "2021-04-25",
  passwords: [ {user: "foo", password: "bar", count: 15}, ... ]},
  {date: "2021-04-26",
  passwords: [ {user: "foo", password: "bar", count: 6}, ... ]}]"""

if __name__ == '__main__':
    # !/usr/bin/env python3
    import operator
    import glob
    import os

    # necessary for remote execution
    if os.getcwd() == "/root":  # we check if current directory is /root so we know we are on a digitalocean node
        LOG_FILE_PATH = "/home/cowrie/cowrie/var/log/cowrie/"

    start = time.time()
    filesize = 0

    input_files = []
    folder_path = Path(LOG_FILE_PATH)

    for file_path in folder_path.glob('**/*.json.*'):
        filename = os.path.basename(file_path)
        if '.mapped' in filename or '.reduced' in filename:
            # don't use already processed files
            # result = filename.rsplit('.', 1)[0]
            # print(result)

            # if result in input_files:
            #    input_files.remove(result)
            continue
        else:
            input_files.append(file_path)

    if len(input_files) == 0:
        print(f"{bcolors.FAIL} Error: No log files found in... {folder_path.absolute()} {bcolors.ENDC}")
        exit(0)

    for file in input_files:
        filesize += os.path.getsize(file)

    mapper = MapReduce(Map().map_func, Reduce().reduce_func)

    log_data = []
    log_data = run_map_reduce(sorted(input_files), mapper)

    #    #as orjson is just able to write binary to file, but we lose FORMATTING then...
    #    with open('reduced.json', 'wb') as f:
    #        f.write(orjson.dumps(log_data, orjson.OPT_INDENT_2))
    #        if len(log_data) > 0:
    #            print(f"{bcolors.OKGREEN} created 'reduced.json' file with cummulated log data{bcolors.ENDC}")
    #        else:
    #            print(log_data)
    #            print(f"{bcolors.FAIL} failed to create 'reduced.json' properly... please check manually {bcolors.ENDC}")

    write_to_file('reduced.json', log_data, 'w')

    end = time.time()
    filesize = filesize / 1000000

    print(f"{bcolors.HEADER} Creating visualization.. {bcolors.ENDC}")
    os.system("python visualize.py reduced.json")
    print(f"{bcolors.OKGREEN} created 'result.html' visualization {bcolors.ENDC}")

    print(f"{bcolors.HEADER} Results {bcolors.ENDC}")
    print(str(len(input_files)) + " log-files")
    print("total size:      {:10.2f} MB".format(filesize))
    print("Analysis:  \t     {:10.2f} s {:10.2f} min".format((end - start), (end - start) / 60))
    print("Speed:     \t     {:10.2f} MB/s".format(filesize / (end - start)))
