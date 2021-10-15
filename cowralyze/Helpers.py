import orjson
import os
from pathlib import Path
import sys
cwd = str(Path(__file__).parent)
sys.path.insert(0, cwd)

# cowrie events
class cEvent:
    """The cEvent object contains functionality to retrieve (Cowrie) Log File Events."""
    LOGIN = 'cowrie.login'
    CONNECT = 'cowrie.session.connect'
    FILE_DOWNLOAD = 'cowrie.session.file_download'
    FILE_UPLOAD = 'cowrie.session.file_upload'
    VIRUS_TOTAL = 'cowrie.virustotal.scanfile'
    COMMAND_INPUT = 'cowrie.command.input'
    CLIENT_VERSION = 'cowrie.client.version'
    CLIENT_SIZE = 'cowrie.client.size'                      # terminal window size
    CLIENT_SSH_FINGERPRINT = 'cowrie.client.fingerprint'    # login via SSH public key
    DIRECT_TCPIP_PROXYING = 'cowrie.direct-tcpip.request'   # proxying request
    DIRECT_TCPIP_DATA_SEND = 'cowrie.direct-tcpip.data'     # data attempted to be sent through our server
    SESSION_CLOSED = 'cowrie.session.closed'                # duration of session: Robot or Human?

    # not part of cowrie
    PRE_DISCONNECT_COMMAND = 'pre_disconnect_command'


class bcolors:
    """The bcolors object contains functionality to beautify the command line output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_files_from_path(path, useLogFiles=True, useMappedFiles=False, useReducedFiles=False):
    """Fetch log files in format *.json.* from specified directory.
      Args:
          path            (str):     Path of folder to be searched recursively.
          useLogFiles     (Boolean): Find and retrieve standard cowrie log files.
          useMappedFiles  (Boolean): Find and retrieve .mapped files.
          useReducedFiles (Boolean): Find and retrieve .reduced files.

      Returns:
          input_files     (list):    List of found input files according to Args specified.
      """
    input_files = []
    for file_path in path.glob('**/*.json.*'):
        filename = os.path.basename(file_path)

        mapped_file = '.mapped' in filename
        reduced_file = '.reduced' in filename
        if mapped_file or reduced_file:
            if mapped_file:
                if useMappedFiles:
                    input_files.append(file_path)
                    continue
            if reduced_file:
                if useReducedFiles:
                    input_files.append(file_path)
                    continue
        else:
            if useLogFiles:
                input_files.append(file_path)

    if len(input_files) == 0:
        print(f"{bcolors.FAIL} Error: No log files found in... {path.absolute()} {bcolors.ENDC}")
        exit(1)

    return input_files


def add_to_dictionary(d, key, val):
    """Add value to dictionary if key is existing or create new key if not.
      Args:
          d   (dict): Dictionary to add key, value pair to.
          key  (Any): Identifier.
          val  (Any): Value.

      Returns:
          input_files     (list):    List of found input files according to Args specified.
      """
    if key in d:
        d[key].append(val)  # use honeypot = sensor as key
    else:
        elements = [val]
        d.update({key: elements})  # add key if not existing already


def key_exists_arr(d, key):
    """Check if key exists in dictionary and return values.
      Args:
          d         (dict): Dictionary which might contain key.
          key        (Any): Identifier.

      Returns:
          d[key]    (list): Values of specified key.
    """
    if key in d:
        return d[key]
    else:
        return []


def key_exists(dic, key):
    """Check if key exists in dictionary and return Boolean.
      Args:
          d         (dict): Dictionary which might contain key.
          key        (Any): Identifier.

      Returns:
          Boolean         : Whether dictionary contains key.
    """
    if key in dic:
        return True
    else:
        return False


def write_to_file(filename, result, mode):
    """Write a json result to a specified filename according to mode.
      Args:
          filename (str): Output filename, e.g. result.json
          result   (Any): JSON result to write to output filename.
          mode     (str): Character to identify file write mode, 'a' .. append, 'w' .. write and so on.
    """
    import json
    with open(filename, mode) as f:
        json.dump(result, f, indent=2)

        if len(result) > 0:
            print(f"{bcolors.OKGREEN} created {filename} {bcolors.ENDC}")
        else:
            print(f"{bcolors.WARNING} {filename} contains no data... please check manually {bcolors.ENDC}")


def build_json(data):
    """Create proper json from list of mapreduced cowrie log file/s data.
       Args:
           data            (list):     List of map-reduced cowrie log file data.
       Returns:
           result_json     (list):    List of proper json formatted data.
    """
    # sort counts of elements descending
    result_json = []  # structured by proper json format
    for key in data.keys():
        date = key[0]
        sensor = key[1]

        temp = {}
        for element in data[key]:
            event = element['event']
            element.pop('event', None)  # remove event type for every entry
            add_to_dictionary(temp, event, element)

        obj = {'date': date, 'sensor': sensor}
        for event in temp.keys():
            res = temp[event]
            if event.startswith(cEvent.LOGIN):
                obj['passwords'] = res
            if event.startswith(cEvent.COMMAND_INPUT):
                obj['commands'] = res
            if event.startswith(cEvent.CONNECT):
                obj['connect'] = res
            if event.startswith(cEvent.SESSION_CLOSED):
                obj['session_closed'] = res
            if event.startswith(cEvent.PRE_DISCONNECT_COMMAND):
                obj['pre_disconnect_command'] = res
            if event.startswith(cEvent.FILE_DOWNLOAD):
                obj['file_download'] = res
            if event.startswith(cEvent.FILE_UPLOAD):
                obj['file_upload'] = res
            if event.startswith(cEvent.DIRECT_TCPIP_PROXYING):
                obj['proxy_request'] = res
        result_json.append(obj)

    if len(result_json) == 1:
        # introduced to reduce RAM on remote execution (as only 1GB RAM)
        # so better to use single object remotely than whole bulk at once
        return result_json[0]
    else:
        return result_json


def get_top_n_events(dict, n):
    top_n = []
    for key in dict.keys():
        top_n = top_n + dict[key][:n]  # concat lists
    return top_n


def split_data_by_events(counts, n):
    n = int(n)

    # build json from MapReduce data
    login_events = {}
    input_events = {}
    pre_disconnect_events = {}
    session_duration_events = {}
    connect_events = {}
    download_file_events = {}
    upload_file_events = {}
    proxy_request_events = {}

    # print(counts)
    for elem, count in counts:
        obj = orjson.loads(elem)

        event = obj['event']
        date = obj['date']
        sensor = obj['sensor']

        if event.startswith(cEvent.LOGIN):
            add_to_dictionary(login_events, (date, sensor), (elem, count))
        if event.startswith(cEvent.COMMAND_INPUT):
            add_to_dictionary(input_events, (date, sensor), (elem, count))
        if event.startswith(cEvent.CONNECT):
            add_to_dictionary(connect_events, (date, sensor), (elem, count))
        if event.startswith(cEvent.SESSION_CLOSED):
            add_to_dictionary(session_duration_events, (date, sensor), (elem, count))
        if event.startswith(cEvent.PRE_DISCONNECT_COMMAND):
            add_to_dictionary(pre_disconnect_events, (date.split('T')[0], sensor), (elem, count))
        if event.startswith(cEvent.FILE_DOWNLOAD):
            add_to_dictionary(download_file_events, (date, sensor), (elem, count))
        if event.startswith(cEvent.FILE_UPLOAD):
            add_to_dictionary(upload_file_events, (date, sensor), (elem, count))
        if event.startswith(cEvent.DIRECT_TCPIP_PROXYING):
            add_to_dictionary(proxy_request_events, (date, sensor), (elem, count))

    top_n_events = []
    top_n_events.append(get_top_n_events(login_events, n))
    top_n_events.append(get_top_n_events(input_events, n))
    top_n_events.append(get_top_n_events(pre_disconnect_events, n))
    top_n_events.append(get_top_n_events(connect_events, n))
    top_n_events.append(get_top_n_events(session_duration_events, n))
    top_n_events.append(get_top_n_events(download_file_events, n))
    top_n_events.append(get_top_n_events(upload_file_events, n))
    top_n_events.append(get_top_n_events(proxy_request_events, n))

    data = {}
    for event_list in top_n_events:
        for element, count in event_list:
            elem = orjson.loads(element)
            event = elem['event']
            date = elem['date']
            sensor = elem['sensor']

            obj = {'event': event}
            if event.startswith(cEvent.LOGIN):
                obj['username'] = elem['username']
                obj['password'] = elem['password']
                obj['count'] = count
            if event.startswith(cEvent.CONNECT):
                obj['src_ip'] = elem['src_ip']
                obj['dst_port'] = elem['dst_port']
                obj['count'] = count
            if event.startswith(cEvent.SESSION_CLOSED):
                obj['src_ip'] = elem['src_ip']
                # obj['session'] = elem['session']
                # obj['duration'] = elem['duration']
                obj['robot'] = elem['robot']
                obj['count'] = count
            if event.startswith(cEvent.COMMAND_INPUT):
                obj['input'] = elem['input']
                obj['count'] = count
            if event.startswith(cEvent.PRE_DISCONNECT_COMMAND):
                obj['input'] = elem['input']
                obj['count'] = count
            if event.startswith(cEvent.FILE_DOWNLOAD):
                obj['url'] = elem['url']
                obj['outfile'] = elem['outfile']
                obj['scans'] = elem['scans']
                obj['count'] = count
            if event.startswith(cEvent.FILE_UPLOAD):
                obj['filename'] = elem['filename']
                # obj['src_ip'] = elem['src_ip']
                obj['count'] = count
            if event.startswith(cEvent.DIRECT_TCPIP_PROXYING):
                obj['src_ip'] = elem['src_ip']
                obj['dst_ip'] = elem['dst_ip']
                obj['dst_port'] = elem['dst_port']
                obj['count'] = count
            add_to_dictionary(data, (date, sensor), obj)
    return data
