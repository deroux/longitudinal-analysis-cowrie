import sys
import time
from pathlib import Path

from MapReduce import MapReduce
from Helpers import cEvent, bcolors, build_json, write_to_file, get_files_from_path
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


def run_map_reduce(files, mapper, n):
    # main work
    counts = mapper(files)
    counts.sort(key=operator.itemgetter(1))
    counts.reverse()

    helper = json_help()
    data = helper.split_data_by_events(counts, n)
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

    # apparently someone provided a log path so let's use this one
    if len(sys.argv) > 1:
        LOG_FILE_PATH = sys.argv[1]
    if len(sys.argv) > 2:
        n = int(sys.argv[2])

    # necessary for remote execution
    if os.getcwd() == "/root":  # we check if current directory is /root so we know we are on a digitalocean node
        LOG_FILE_PATH = "/home/cowrie/cowrie/var/log/cowrie/"

    start = time.time()
    filesize = 0

    input_files = []
    folder_path = Path(LOG_FILE_PATH)

    input_files = get_files_from_path(folder_path)

    for file in input_files:
        filesize += os.path.getsize(file)

    mapper = MapReduce(Map().map_func, Reduce().reduce_func)
    log_data = []
    log_data = run_map_reduce(sorted(input_files), mapper, n)
    write_to_file('reduced.json', log_data, 'w')

    end = time.time()
    filesize = filesize / 1000000

    print(f"{bcolors.HEADER} Results {bcolors.ENDC}")
    print(str(len(input_files)) + " log-files")
    print("total size:      {:10.2f} MB".format(filesize))
    print("Analysis:  \t     {:10.2f} s {:10.2f} min".format((end - start), (end - start) / 60))
    print("Speed:     \t     {:10.2f} MB/s".format(filesize / (end - start)))
    sys.exit(0)
