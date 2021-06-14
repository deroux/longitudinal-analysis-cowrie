import plotly.graph_objects as go
import sys
import orjson
from collections import Counter

from Helpers import add_to_dictionary


def print_session_trace(file_path, session_id):
    session_trace = []
    with open(file_path, 'rt') as f:
        for line in f:
            js = orjson.loads(line)
            session = js.get('session')

            if session_id == session:
                session_trace.append(js)

    # sort (normally sorted but to be sure)
    session_trace.sort(key=lambda k: (k['timestamp']), reverse=False)

    events = []
    labels = []
    values = []

    for element in session_trace:
        events.append(element['eventid'])
        labels.append(element['message'])
        values.append(100)

    source = [i for i in range(len(labels) - 1)]
    target = [i + 1 for i in range(len(labels) - 1)]

    link = dict(source=source, target=target, value=values, label=events)
    node = dict(label=labels)
    data = go.Sankey(link=link, node=node, orientation='v')

    fig = go.Figure(data)
    fig.update_layout(
        hovermode='x',
        title_text=f"Session trace for id: {session_id}<br>Source: {file_path}",
        font=dict(color='white'),
        paper_bgcolor='#51504f')
    fig.show()


def print_ip_many_session_trace(file_path, ip_address):
    session_trace = []
    with open(file_path, 'rt') as f:
        for line in f:
            js = orjson.loads(line)
            src_ip = js.get('src_ip')

            if src_ip == ip_address:
                session_trace.append(js)

    # sort (normally sorted but to be sure)
    session_trace.sort(key=lambda k: (k['timestamp']), reverse=False)

    events = []
    labels = []
    values = []

    known_sessions = {}
    source = []
    target = []

    counter = 0
    my_dict = {}
    for element in session_trace:
        add_to_dictionary(my_dict, element['session'], element)

    elements_count = 0
    for key in my_dict.keys():
        elements = my_dict[key]
        elements_count += len(elements)
        # add new path for each session
        for element in elements:
            if element['eventid'] == 'cowrie.session.params':
                if len(element['message']) == 0:
                    element['message'].append('Event: cowrie.session.params')
                    # todo : not sure if we need this

            events.append(element['eventid'])
            labels.append(element['message'])
            values.append(1)

            # so we get own path for each session here
            if counter < elements_count - 1:
                source.append(counter)
                target.append(counter + 1)

            counter += 1

    link = dict(source=source, target=target, value=values, label=events)
    node = dict(label=labels)
    data = go.Sankey(link=link, node=node, orientation='v')

    fig = go.Figure(data)
    fig.update_layout(
        hovermode='x',
        title_text=f"Session trace for ip: {src_ip}<br>Source: {file_path}",
        font=dict(color='white'),
        paper_bgcolor='#51504f')
    fig.show()


if __name__ == "__main__":
    # !/usr/bin/env python3
    if len(sys.argv) != 3:
        print(
            f"Invalid number of arguments. Type 'python {sys.argv[0]} <LOG_FILE_PATH/cowrie.json.YYYY-MM-DD> <session_id>")

    filename = sys.argv[1]
    session_id = sys.argv[2]

    print_session_trace(filename, session_id)
    # print_ip_many_session_trace(filename, '104.131.48.26')
