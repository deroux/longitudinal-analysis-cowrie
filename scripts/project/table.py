import operator

from rich.console import Console
from rich.table import Column, Table
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
