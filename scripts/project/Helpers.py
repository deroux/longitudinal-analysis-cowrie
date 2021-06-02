import orjson


# cowrie events
class cEvent:
    LOGIN = 'cowrie.login'
    CONNECT = 'cowrie.session.connect'
    FILE_DOWNLOAD = 'cowrie.session.file_download'
    FILE_UPLOAD = 'cowrie.session.file_upload'
    VIRUS_TOTAL = 'cowrie.virustotal.scanfile'
    COMMAND_INPUT = 'cowrie.command.input'
    CLIENT_VERSION = 'cowrie.client.version'
    CLIENT_SIZE = 'cowrie.client.size'  # terminal window size
    CLIENT_SSH_FINGERPRINT = 'cowrie.client.fingerprint'  # login via SSH public key
    DIRECT_TCPIP_PROXYING = 'cowrie.direct-tcpip.request'  # proxying request
    DIRECT_TCPIP_DATA_SEND = 'cowrie.direct-tcpip.data'  # data attempted to be sent through our server
    SESSION_CLOSED = 'cowrie.session.closed' # to find out duration of session

    # not part of cowrie
    PRE_DISCONNECT_COMMAND = 'pre_disconnect_command'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def add_to_dictionary(dict, key, value):
    if key in dict:
        dict[key].append(value)  # use honeypot = sensor as key
    else:
        elements = [value]
        dict.update({key: elements})  # add key if not existing already


def build_json(data):
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

    return list(result_json)


class json_help:
    def __init__(self):
        pass

    def get_top_n_events(self, dict, n):
        top_n = []
        for key in dict.keys():
            top_n = top_n + dict[key][:n]  # concat lists
        return top_n

    def split_data_by_events(self, counts):
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

        n = 3
        top_n_events = []
        top_n_events.append(self.get_top_n_events(login_events, n))
        top_n_events.append(self.get_top_n_events(input_events, n))
        top_n_events.append(self.get_top_n_events(pre_disconnect_events, n))
        top_n_events.append(self.get_top_n_events(connect_events, n))
        top_n_events.append(self.get_top_n_events(session_duration_events, n))
        top_n_events.append(self.get_top_n_events(download_file_events, n))
        top_n_events.append(self.get_top_n_events(upload_file_events, n))
        top_n_events.append(self.get_top_n_events(proxy_request_events, n))

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
                    obj['src_ip'] = elem['src_ip']
                    obj['count'] = count
                if event.startswith(cEvent.DIRECT_TCPIP_PROXYING):
                    obj['src_ip'] = elem['src_ip']
                    obj['dst_ip'] = elem['dst_ip']
                    obj['dst_port'] = elem['dst_port']
                    obj['count'] = count
                add_to_dictionary(data, (date, sensor), obj)
        return data
