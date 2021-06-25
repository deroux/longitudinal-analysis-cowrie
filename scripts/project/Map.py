#!/usr/bin/python
import multiprocessing
import sys, os
import orjson, json  # as json is more conventient for writing to file, orjson faster
from pathlib import Path

from Helpers import cEvent, get_files_from_path

global MAX_ROBOT_TIME, LOG_FILE_PATH

try:
    with open("config.json") as json_data_file:
        data = json.load(json_data_file)
        MAX_ROBOT_TIME = float(data["settings"]["robot_max_time"])
        LOG_FILE_PATH = data["settings"]["log_file_path"]
except Exception as e:
    # fallback if config file not found
    MAX_ROBOT_TIME = 10.0
    LOG_FILE_PATH = './'
    print(e)
    pass


class Map:
    """The Map object contains functionality to Map a log file according to the MapReduce programming model

       Args:
        filename (str): The filename of a cowrie generated log file like e.g. cowrie.json.2021-05-03 to perform map operation on.
    """
    def __init__(self):
        self.detailedAntivirus = False  # enable this to see in output .json which antivir scanners have POSITIVEd our file
        self.urlFilesOnly = False  # output of 'file_download' checks for files with available URL only
        self.detailedOutput = False

    def map_func(self, filename):
        """Read a cowrie log file and return a sequence of various (command, occurences) values.
        Args:
            filename (str): Filename of log file in format cowrie.json.YYYY-MM-DD

        Returns:
            output: List of Tuples with data mapped to 1 for later reduction step.
            e.g. (b'{"date":"2021-05-01","sensor":"ubuntu-18-04-lts-honeypot-01","event":"cowrie.session.connect","src_ip":"37.120.212.4","dst_port":2222}', 1)
        """
        if self.detailedOutput:
            print(multiprocessing.current_process().name, 'reading', filename)

        output = []
        # for commands before disconnect
        pre_disconnect_commands = {}
        downloaded_files = {}
        virus_scans = {}

        with open(filename, 'rt') as f:
            for line in f:
                try:
                    js = orjson.loads(line)
                except Exception as e:
                    print(e)
                    continue
                    pass

                event = js.get('eventid')

                timestamp = js.get('timestamp')  # 2021-05-01T14:52:22.329173Z
                date = timestamp.split('T')[0]  # 2021-05-01
                sensor = js.get('sensor')
                session = js.get('session')

                el = {'date': date, 'sensor': sensor, 'event': event}
                if cEvent.LOGIN in event:
                    el['event'] = cEvent.LOGIN  # as we need cowrie.login.failed and cowrie.login.sucess => cowrie.login
                    el['username'] = js.get('username')
                    el['password'] = js.get('password')
                    output.append((orjson.dumps(el), 1))
                    continue

                if cEvent.CONNECT in event:
                    el['src_ip'] = js.get('src_ip')
                    el['dst_port'] = js.get('dst_port')
                    output.append((orjson.dumps(el), 1))
                    continue

                if cEvent.SESSION_CLOSED in event:
                    duration = js.get('duration')
                    # todo make configurable
                    if duration < MAX_ROBOT_TIME:  # most likely robot
                        el['robot'] = True
                    else:
                        el['robot'] = False
                    el['src_ip'] = js.get('src_ip')
                    # el['duration'] = js.get('duration')
                    # el['session'] = js.get('session')
                    output.append((orjson.dumps(el), 1))
                    continue

                if cEvent.DIRECT_TCPIP_PROXYING in event:
                    el['src_ip'] = js.get('src_ip')
                    el['dst_ip'] = js.get('dst_ip')
                    el['dst_port'] = js.get('dst_port')
                    output.append((orjson.dumps(el), 1))
                    continue

                if cEvent.FILE_UPLOAD in event:
                    el['filename'] = js.get('filename')
                    el['src_ip'] = js.get('src_ip')
                    output.append((orjson.dumps(el), 1))

                if cEvent.FILE_DOWNLOAD in event:
                    el['url'] = js.get('url')
                    el['outfile'] = js.get('outfile')
                    el['shasum'] = js.get('shasum')

                    # if we want externally downloaded files only
                    if self.urlFilesOnly:
                        if el['url'] == '' or el['url'] == None:
                            continue

                    # necessary to take shasum for occurence of multiple files
                    downloaded_files[(session, el['shasum'])] = el
                    continue

                if cEvent.VIRUS_TOTAL in event:  # let's check whether the uploaded file contained malware using virustotal report
                    el['sha256'] = js.get('sha256')
                    el['positives'] = js.get('positives')
                    el['total'] = js.get('total')

                    if self.detailedAntivirus:
                        el['scans'] = js.get('scans')

                    virus_scans[(session, el['sha256'])] = el
                    continue

                if cEvent.COMMAND_INPUT in event:
                    # regular commands
                    el['input'] = js.get('input')
                    output.append((orjson.dumps(el), 1))

                    # find pre_disconnect_commands
                    # check already executed commands in session and check for latest timestamp
                    el['event'] = cEvent.PRE_DISCONNECT_COMMAND
                    if session in pre_disconnect_commands:
                        # compare
                        old_timestamp = pre_disconnect_commands[session]['timestamp']
                        new_timestamp = js.get('timestamp')
                        if old_timestamp < new_timestamp:
                            el['timestamp'] = new_timestamp
                            pre_disconnect_commands[session] = el
                    else:
                        el['timestamp'] = timestamp
                        pre_disconnect_commands[session] = el

            for key in virus_scans.keys():
                if key in downloaded_files:
                    el = {'positives': virus_scans[key]['positives'], 'total': virus_scans[key]['total']}
                    if self.detailedAntivirus:
                        el['scans'] = virus_scans[key]['scans']
                    downloaded_files[key]['scans'] = el
                    output.append((orjson.dumps(downloaded_files[key]), 1))

            for val in pre_disconnect_commands.values():
                # remove timestamp entries to aggregate same input command values afterwards
                val.pop('timestamp', None)
                output.append((orjson.dumps(val), 1))
        return output


def run_map(filename, mode):
    """Runner to read a cowrie log file and return a sequence of various (command, occurences) values.
    Args:
        filename (str): Filename of log file in format cowrie.json.YYYY-MM-DD

    Returns:
        output: Mapped file of input data in format cowrie.json.YYYY-MM-DD.mapped
    """
    import orjson
    from Map import Map
    from Helpers import write_to_file

    print(f"Map on: {filename}")

    if os.path.exists(f'{filename}.mapped'):
        if 'c' in mode:
            # continue on filename.mapped already existing
            print(f"Already existing, using: {filename}.mapped")
            return

    try:
        mapped = Map().map_func(filename)
        out = []
        for tup in mapped:
            obj = {'log': orjson.loads(tup[0]), 'count': 1}
            out.append(obj)

        outFile = str(filename) + '.mapped'
        write_to_file(outFile, out, 'w')

    except Exception as e:
        print(e)
        pass


if __name__ == "__main__":
    # !/usr/bin/env python3
    """Main function to read a cowrie log file and return a sequence of various (command, occurences) values.
    
    Params:
        filename (str): Filename of log file in format cowrie.json.YYYY-MM-DD

    Returns:
        output: Mapped file of input data in format cowrie.json.YYYY-MM-DD.mapped
    """
    # necessary for remote execution
    if os.getcwd() == "/root":  # we check if current directory is /root so we know we are on a digitalocean node
        LOG_FILE_PATH = "/home/cowrie/cowrie/var/log/cowrie/"

    if len(sys.argv) == 3:
        file = sys.argv[1]
        mode = sys.argv[2]
        run_map(file, mode)
    else:
        # Fall back, try to use all files in current directory
        folder_path = Path(LOG_FILE_PATH)
        input_files = get_files_from_path(folder_path)
        for file in input_files:
            run_map(file, 'c') # default mode, continue on already existing