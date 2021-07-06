import multiprocessing
import os
import click
import pyfiglet
import tqdm

from Map import run_map
from Reduce import run_reduce
from Remote import deploy_exec_remote, fetch_from_remote
from Combine import combine_reduced_files
from table import create_output_table
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
    f = pyfiglet.Figlet(font='slant')
    print(f.renderText('cowralyze'))
    pass

@click.command()
@click.option('--ip', '-i', required=True, multiple=True, help="IP Address of remote droplet")
@click.option('--port', '-p', required=True, multiple=True, help="Port of remote droplet (real SSH port of server, not cowrie port)")
@click.option('--user', '-u', default=['root'], multiple=True, help="Login username of remote droplet")
@click.option('--pw', '-pw', required=True, multiple=True, help="Login password of remote droplet")
@click.option('--top_n_events', '-n', default=[5], multiple=True, help='Reduce & visualize top n occurring events in cowrie log files')
@click.option('--logfile', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def analyze_remote(ip, port, user, pw, top_n_events, logfile, outfile):
    """Map-Reduce all log files on remote cowrie node, download reduced.json, create result.html for visualization."""
    # python3 cli.py analyze-remote -i 104.248.245.133 -i 104.248.253.81 -p 2112 -p 2112 -pw 16Sfl,Rkack -pw 16Sfl,Rkack
    pool = multiprocessing.Pool(multiprocessing.cpu_count() * 2)
    log_files = []
    items = []
    for i, val in enumerate(ip):
        _ip = val
        _port = port[i-1]
        _user = user[i-1]
        _pw = pw[i-1]
        _top_n_events = top_n_events[i-1]
        items.append((_ip, _port, _user, _pw, _top_n_events))

    for _ in tqdm.tqdm(pool.starmap(run_remote, items), total=len(ip)):
        log_files.append(_)
        pass

    if len(log_files) > 1:
        combine_reduced_files(log_files, logfile)
    else:
        logfile = log_files.pop()

    call_visualization(logfile, outfile)


def run_remote(ip, port, user, pw, top_n_events):
    deploy_exec_remote(ip, port, user, pw, top_n_events)
    logfile = fetch_from_remote(ip, port, user, pw)
    return logfile

@click.command()
@click.option('--path', '-p', required=True, type=click.Path(exists=True), help="Local folder path to look for log files to map reduce and analyze")
@click.option('--logfile', '-f', default='reduced.json', help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
@click.option('--top_n_events', '-n', default=5, help='Reduce & visualize top n occurring events in cowrie log files')
def analyze_local(path, logfile, outfile, top_n_events):
    """Map-Reduce all log files in local folder, create reduced.json, create result.html for visualization."""
    # python cli.py analyze-local -p C:\Users\Dominic\Documents\longitudinal-analysis-cowrie\scripts\project\logs
    os.system(f"python Local.py {path} {top_n_events}")
    call_visualization(logfile, outfile)


@click.command()
@click.option('--file', '-f', required=True, help='Filename of cowrie log file to map')
@click.option('--mode', '-m', default='w', help='Behaviour on already existing mapped file: c=continue, w=overwrite')
def map(file, mode):
    """Map local log file and create LOG_FILE.mapped"""
    # python cli.py map-file -f logs_mini/cowrie.json.2021-05-03
    run_map(file, mode)


@click.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True)) # help="Local file/s to perform REDUCE operation on."
@click.option('--outfile', '-o', default='reduced.json', help='Filename of reduced data *.json')
@click.option('--top_n_events', '-n', default=5, help='Reduce & visualize top n occurring events in cowrie log files')
@click.option('--mode', '-m', default='w', help='Behaviour on already existing reduced file: c=continue, w=overwrite')
def reduce(files, outfile, top_n_events, mode):
    """Reduce local log file/s and create reduced.json and REDUCED_FILE.reduced for further usage
     Params:
         files    (str, n): Filename/s of .mapped files to reduce
     """
    # python cli.py reduce-file logs_mini/cowrie.json.2021-05-03.mapped logs_mini/cowrie.json.2021-05-04.mapped # ... possibly n files
    run_reduce(files, outfile, top_n_events, mode)

@click.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--outfile', '-o', default='reduced.json', help='Filename of final output *.json')
def combine_reduced(files, outfile):
    """Combine reduced.json files from multiple nodes to single reduced.json
     Params:
         files    (str, n): Filename/s of result.json files to combine
         outfile     (str): Filename of final output *.json
     Returns:
         Creates file.json with combined reduced file data
     """
    # python cli.py combine-reduced 104.248.245.133_reduced.json 104.248.253.81_reduced.json .... -o test.json
    combine_reduced_files(files, outfile)


@click.command()
@click.option('--logfile', '-f', required=True, type=click.Path(exists=True), help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='result.html', help='Filename of result visualization *.html')
def visualize(logfile, outfile):
    """Use reduced.json file and create result.html visualization out of it"""
    call_visualization(logfile, outfile)


def call_visualization(logfile, outfile):
    os.system(f"python visualize.py {logfile} {outfile}")
    create_output_table(logfile)

@click.command()
@click.option('--logfile', '-f', required=True, type=click.Path(exists=True), help='Filename of reduced log file of generated *.json')
@click.option('--outfile', '-o', default='statistics.html', help='Filename of result visualization *.html')
def statistics(logfile, outfile):
    """Use reduced.json file and create statistics.html visualization out of it"""
    call_statistics(logfile, outfile)


def call_statistics(logfile, outfile):
    os.system(f"python stats.py {logfile} {outfile}")



@click.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Filename of log file to find session id in and create trace of commands executed')
@click.option('--session_id', '-sid', required=True, help='Session ID for specific session trace of interest')
def trace_sid(file, session_id):
    """Use cowrie.json.YYYY-MM-DD file and Session ID to trace commands executed"""
    # python cli.py trace-sid -f logs\honeypot-a\cowrie.json.2021-05-01 -sid 8b7feeeacafd
    print_session_trace(file, session_id)


@click.command()
@ click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Filename of log file to find session id in and create trace of commands executed')
@ click.option('--ip', '-i', required=True, help='Session ID for specific session trace of interest')
def trace_ip(file, ip):
    """Use cowrie.json.YYYY-MM-DD file and IP to trace commands executed"""
    # python cli.py trace-sid -f logs\honeypot-a\cowrie.json.2021-05-01 -sid 104.131.48.26
    print_ip_many_session_trace(file, ip)


cli.add_command(analyze_remote)
cli.add_command(analyze_local)
cli.add_command(map)
cli.add_command(reduce)
cli.add_command(combine_reduced)
cli.add_command(visualize)
cli.add_command(statistics)
cli.add_command(trace_sid)
cli.add_command(trace_ip)

if __name__ == "__main__":
    # !/usr/bin/env python3
    cli()
