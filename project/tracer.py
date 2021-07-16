import json
import operator

import plotly.graph_objects as go
import sys
import orjson

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


def longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2))] * (1 + len(s1))
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


def sankey_plot_inputs(file_path):
    session_inputs = {}
    with open(file_path, 'rt') as f:
        for line in f:
            js = orjson.loads(line)

            if js.get('eventid') == 'cowrie.command.input':
                add_to_dictionary(session_inputs, js.get('session'), (js.get('input'), js.get('timestamp')))

    """
    for lst in session_inputs.values():
        rel_pos = -1       # to know when command has been executed in session
        for tup in lst:
            input, timestamp = tup
            rel_pos += 1

            if rel_pos > max_rel_pos:
                max_rel_pos = rel_pos

            if (input, rel_pos) in counter:
                counter[(input, rel_pos)] += 1
            else:
                counter[(input, rel_pos)] = 1

    sortlist = sorted(counter.items(), key=operator.itemgetter(1), reverse=True)
    """
    source_target_value = {}

    for lst in session_inputs.values():
        num_commands = len(lst)
        for i in range(num_commands):
            input, timestamp = lst[i]

            if i == 0:
                key = (input, None)

            if i + 1 < num_commands:
                input_next, timestamp_next = lst[i + 1]
                key = (input, input_next)

                # TODO: accumulate similar commands when only 1 appeared
                # e.g. compare first 15 chars >> probably same command

            if key in source_target_value:
                source_target_value[key] += 1
            else:
                source_target_value[key] = 1

    sortlist = sorted(source_target_value.items(), key=operator.itemgetter(1), reverse=True)

    for key, value in sortlist:
        if value > 1:
            print(key, ' : ', value)

    labels = []
    sources = []
    targets = []
    values = []

    feeder = []

    for key, value in sortlist:
        source_cmd, target_cmd = key
        val = value

        if val < 1:
            continue

        labels.append(f'{source_cmd} : {val}')

        if source_cmd not in feeder:
            feeder.append(source_cmd)
        if target_cmd not in feeder:
            feeder.append(target_cmd)

        sources.append(feeder.index(source_cmd))
        targets.append(feeder.index(target_cmd))
        values.append(val)

    """
            for el in feeder:
                lcs = longest_common_substring(el, source_cmd)
                if len(lcs)  > 5:
                    print(source_cmd)
                    print(lcs)
    """

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=30,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                ),
                link=dict(
                    # flow source node index
                    source=sources,
                    # flow target node index
                    target=targets,
                    # flow quantity for each source/target pair
                    value=values,
                )
            )
        ]
    )

    # fig.update_layout(width=auto, height=auto)
    fig.show()

    # sort (normally sorted but to be sure)
    """
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
    """


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
    # session_id = sys.argv[2]

    # print_session_trace(filename, session_id)
    # print_ip_many_session_trace(filename, session_id)
    sankey_plot_inputs(filename)
