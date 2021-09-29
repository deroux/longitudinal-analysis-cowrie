import sys

from tabulate import tabulate

from rich.console import Console
from rich.table import Table
import json

from Helpers import key_exists


def create_output_table(file):
    console = Console()

    f = open("result.log", "w")

    my_data = []
    console.log(file)
    with open(file) as json_file:
        data = json.load(json_file)
        try:
            data = sorted(data, key=lambda k: k['date'], reverse=True)
        except Exception as e:
            print(e)
            pass

        # Username Password Table
        head = ["Date", "Sensor", "Username", "Password", "Count"]

        for elem in data:
            if key_exists(elem, 'passwords'):
                for el in elem['passwords']:
                    my_data.append([elem['date'], elem['sensor'], el['username'], el['password'], str(el['count'])])

        f.write("User : Password \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")

        # Commands table
        head = ["Date", "Sensor", "Command", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'commands'):
                for el in elem['commands']:
                    inp = el['input']
                    if len(inp) > 100:
                        inp = inp[0 : 100] + '..'

                    my_data.append([elem['date'], elem['sensor'], inp, str(el['count'])])

        f.write("Commands \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")


        # Pre-disconnect commands table
        head = ["Date", "Sensor", "Pre-disconnect-command", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'pre_disconnect_command'):
                for el in elem['pre_disconnect_command']:
                    inp = el['input']
                    if len(inp) > 100:
                        inp = inp[0 : 100] + '..'

                    my_data.append([elem['date'], elem['sensor'], inp, str(el['count'])])

        f.write("Pre-Disconnect-Commands \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")

        # Connect table
        head = ["Date", "Sensor", "Source IP", "Destination Port", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'connect'):
                for el in elem['connect']:
                    my_data.append([elem['date'], elem['sensor'], el['src_ip'], str(el['dst_port']), str(el['count'])])

        f.write("Connects \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")


        # Session closed
        head = ["Date", "Sensor", "Source IP", "Robot", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'session_closed'):
                for el in elem['session_closed']:
                    my_data.append([elem['date'], elem['sensor'], el['src_ip'], str(el['robot']), str(el['count'])])

        f.write("Session-Closed \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")

        # file download
        head = ["Date", "Sensor", "URL", "Positives / Total", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'file_download'):
                for el in elem['file_download']:
                    pos = el['scans']['positives']
                    total = el['scans']['total']
                    my_data.append([elem['date'], elem['sensor'], el['url'], f'{pos} / {total}', str(el['count'])])

        f.write("File download \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")

        # file upload
        head = ["Date", "Sensor", "Filename", "Source IP", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'file_upload'):
                for el in elem['file_upload']:
                    my_data.append([elem['date'], elem['sensor'], el['filename'], el['src_ip'], str(el['count'])])

        f.write("File upload \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")

        # proxy request
        head = ["Date", "Sensor", "Source IP", "Destination IP : PORT", "Count"]
        my_data.clear()
        for elem in data:
            if key_exists(elem, 'proxy_request'):
                for el in elem['proxy_request']:
                    destination = el['dst_ip'] + ':' + str(el['dst_port'])
                    my_data.append([elem['date'], elem['sensor'], el['src_ip'], destination, str(el['count'])])

        f.write("Proxy request \n\n")
        f.write(tabulate(my_data, headers=head, tablefmt="grid"))
        f.write("\n\n")

if __name__ == '__main__':
    # !/usr/bin/env python3
    create_output_table(sys.argv[1])