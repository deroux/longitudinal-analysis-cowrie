import os
import click
from pyfiglet import Figlet
from remote import deploy_exec_remote, fetch_from_remote

__author__ = "d3roux"

from tracer import print_session_trace, print_ip_many_session_trace


@click.group()
def cli():
    """Map-Reduce tool to analyze cowrie log files on remote servers / local over time and create a visualization of the data.

    Uses multiple log files <cowrie.json.YYYY-MM-DD> to create a cummulated
    information file and visualization from local or remote folder path.

    LOCAL: python cli.py analyze-local -p FOLDER_PATH
    REMOTE: python cli.py analyze-remote -i 123.456.789.10 -p 2112 -u root -pw pass
    """
    # f = Figlet(font='slant')
    # print(f.renderText('cowralyze'))
    pass


@click.command()
@click.option('--ip', '-i', help="IP Address of remote droplet")
@click.option('--port', '-p', help="Port of remote droplet (real SSH port of server, not cowrie port)")
@click.option('--user', '-u', default='root', help="Login username of remote droplet")
@click.option('--pw', '-pw', help="Login password of remote droplet")
@click.option('--logfile', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def analyze_remote(ip, port, user, pw, logfile, outfile):
    """Map-Reduce all log files on remote cowrie node, download reduced.json, create result.html for visualization."""
    deploy_exec_remote(ip, port, user, pw)
    fetch_from_remote(ip, port, user, pw)
    call_visualization(logfile, outfile)


@click.command()
@click.option('--path', '-p', default="./", type=click.Path(exists=True), help="Local folder path to look for log files to map reduce and analyze")
@click.option('--logfile', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def analyze_local(path, logfile, outfile):
    """Map-Reduce all log files in local folder, create reduced.json, create result.html for visualization."""
    os.system(f"python Local.py {path}")
    call_visualization(logfile, outfile)


@click.command()
@click.option('--file', '-f', help="Local file to perform MAP operation on.")
def map_file(file):
    """Map local log file and create LOG_FILE.mapped"""
    os.system(f"python Map.py {file}")


@click.command()
@click.argument('files', nargs=-1, type=click.Path()) # help="Local file/s to perform REDUCE operation on."
def reduce_file(files):
    """Reduce local log file/s and create reduced.json and REDUCED_FILE.reduced for further usage"""
    arg = ' '.join(files)
    os.system(f"python Reduce.py {arg}")


@click.command()
@click.option('--logfile', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def visualize(logfile, outfile):
    """Use reduced.json file and create result.html visualization out of it"""
    call_visualization(logfile, outfile)


@click.command()
@click.option('--logfile', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def visualize(logfile, outfile):
    """Use reduced.json file and create result.html visualization out of it"""
    call_visualization(logfile, outfile)


def call_visualization(logfile, outfile):
    os.system(f"python visualize.py {logfile} {outfile}")


@click.command
@click.option('--file', '-f', help='Filename of log file to find session id in and create trace of commands executed')
@click.option('--session_id', '-sid', help='Session ID for specific session trace of interest')
def sid_trace(filename, session_id):
    """Use cowrie.json.YYYY-MM-DD file and Session ID to trace commands executed"""
    print_session_trace(filename, session_id)


@click.command
@ click.option('--file', '-f', help='Filename of log file to find session id in and create trace of commands executed')
@ click.option('--ip', '-i', help='Session ID for specific session trace of interest')
def ip_trace(filename, ip):
    """Use cowrie.json.YYYY-MM-DD file and IP to trace commands executed"""
    print_ip_many_session_trace(filename, ip)


cli.add_command(analyze_remote)
cli.add_command(analyze_local)
cli.add_command(map_file)
cli.add_command(reduce_file)
cli.add_command(visualize)
cli.add_command(sid_trace)
cli.add_command(ip_trace)

if __name__ == "__main__":
    # !/usr/bin/env python3
    cli()
