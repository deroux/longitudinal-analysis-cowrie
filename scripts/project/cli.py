import os
import click
from pyfiglet import Figlet

from Map import run_map
from Reduce import run_reduce
from remote import deploy_exec_remote, fetch_from_remote
from tracer import print_session_trace, print_ip_many_session_trace

__author__ = "deroux"

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
    # python cli.py analyze-local -p C:\Users\Dominic\Documents\longitudinal-analysis-cowrie\scripts\project\logs
    os.system(f"python Local.py {path}")
    call_visualization(logfile, outfile)


@click.command()
@click.option('--file', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
def map_file(file):
    """Map local log file and create LOG_FILE.mapped"""
    # python cli.py map-file -f logs_mini/cowrie.json.2021-05-03
    run_map(file)


@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True)) # help="Local file/s to perform REDUCE operation on."
@click.option('--outfile', '-o', default='reduced.json', help='Filename of reduced data *.json')
def reduce_file(files, outfile):
    """Reduce local log file/s and create reduced.json and REDUCED_FILE.reduced for further usage"""
    # python cli.py reduce-file logs_mini/cowrie.json.2021-05-03.mapped logs_mini/cowrie.json.2021-05-04.mapped # ... possibly n files
    run_reduce(files, outfile)


@click.command()
@click.option('--logfile', '-f', default='reduced.json', type=click.Path(exists=True), help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def visualize(logfile, outfile):
    """Use reduced.json file and create result.html visualization out of it"""
    call_visualization(logfile, outfile)


def call_visualization(logfile, outfile):
    os.system(f"python visualize.py {logfile} {outfile}")


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Filename of log file to find session id in and create trace of commands executed')
@click.option('--session_id', '-sid', help='Session ID for specific session trace of interest')
def trace_sid(file, session_id):
    """Use cowrie.json.YYYY-MM-DD file and Session ID to trace commands executed"""
    # python cli.py trace-sid -f logs\honeypot-a\cowrie.json.2021-05-01 -sid 8b7feeeacafd
    print_session_trace(file, session_id)


@click.command()
@ click.option('--file', '-f', type=click.Path(exists=True), help='Filename of log file to find session id in and create trace of commands executed')
@ click.option('--ip', '-i', help='Session ID for specific session trace of interest')
def trace_ip(file, ip):
    """Use cowrie.json.YYYY-MM-DD file and IP to trace commands executed"""
    # python cli.py trace-sid -f logs\honeypot-a\cowrie.json.2021-05-01 -sid 104.131.48.26
    print_ip_many_session_trace(file, ip)


cli.add_command(analyze_remote)
cli.add_command(analyze_local)
cli.add_command(map_file)
cli.add_command(reduce_file)
cli.add_command(visualize)
cli.add_command(trace_sid)
cli.add_command(trace_ip)

if __name__ == "__main__":
    # !/usr/bin/env python3
    cli()
