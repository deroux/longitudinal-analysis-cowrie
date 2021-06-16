import operator

from rich.console import Console
from rich.table import Column, Table
from tabulate import tabulate

import json

console = Console()
with open('reduced.json') as json_file:
    data = json.load(json_file)

    # Username Password Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Sensor")
    table.add_column("Username", justify="right")
    table.add_column("Password", justify="right")
    table.add_column("Count", justify="right")

    for elem in data:
        for el in elem['passwords']:
            table.add_row(
                elem['date'], elem['sensor'], el['username'], el['password'], str(el['count'])
            )
    console.print(table)

    # Commands table
    records = []
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Sensor")
    table.add_column("Command", justify="right")
    table.add_column("Count", justify="right")

    for elem in data:
        for el in elem['commands']:
            table.add_row(
                elem['date'], elem['sensor'], el['input'], str(el['count'])
            )
    console.print(table)

    # Pre-disconnect commands table
    records = []
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Sensor")
    table.add_column("Pre-disconnect-command", justify="right")
    table.add_column("Count", justify="right")

    for elem in data:
        for el in elem['pre_disconnect_command']:
            table.add_row(
                elem['date'], elem['sensor'], el['input'], str(el['count'])
            )
    console.print(table)

    # Connect table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Sensor")
    table.add_column("Source IP", justify="right")
    table.add_column("Destination Port", justify="right")
    table.add_column("Count", justify="right")

    for elem in data:
        for el in elem['connect']:
            table.add_row(
                elem['date'], elem['sensor'], el['src_ip'], str(el['dst_port']), str(el['count'])
            )
    console.print(table)

    # Session closed
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim", width=12)
    table.add_column("Sensor")
    table.add_column("Source IP", justify="right")
    table.add_column("Robot", justify="right")
    table.add_column("Count", justify="right")

    for elem in data:
        for el in elem['session_closed']:
            table.add_row(
                elem['date'], elem['sensor'], el['src_ip'], str(el['robot']), str(el['count'])
            )
    console.print(table)


    # file download
    # file upload
    # proxy request
