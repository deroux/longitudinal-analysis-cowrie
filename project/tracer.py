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


def longest_common_prefix(a):
    if not a:
        return ''
    prefix = a[0]
    for word in a:
        if len(prefix) > len(word):
            prefix, word = word, prefix

        while len(prefix) > 0:
            if word[:len(prefix)] == prefix:
                break
            else:
                prefix = prefix[:-1]
    return prefix

"""
    import textdistance
    dist = textdistance.levenshtein.normalized_similarity(a, b)
    if dist > 0.8:
        print(a)
        print(b)
        print(dist)
        # find and return longest matching prefix
        a, b = a.strip(), b.strip()
        return True, longest_common_prefix([a,b])
    return False, ''
    """
def similar(a, b):
    from io import StringIO
    buf = StringIO()

    if a == b:
        return True, a
    # We filter out common commands with different subpatterns
    # a = echo "root:gXPbD7x50eAW"|chpasswd|bash
    # b = echo "root:OS4DnVZpKnby"|chpasswd|bash
    # str_out = echo "root:"|chpasswd|bash
    score = 0
    lenA = len(a)
    lenB = len(b)
    stop = lenA

    if lenA == lenB:
        score += 2
    if len(a) > len(b):
        stop = lenB
    if len(a) < len(b):
        stop = lenA

    before_and_after = 0

    for i in range(stop):
        if a[i] == b[i]:
            next_char_match = True
            if i < stop-1:
                next_char_match = a[i + 1] == b[i + 1]
            if next_char_match:
                if before_and_after == 1:
                    before_and_after = 2
                buf.write(a[i])

            score += 1
        else:
            before_and_after = 1
            score -= 1
    if score > 5 and before_and_after == 2:   # filter out e.g. 'echo "root:UIdsK9d9zISe"|chpasswd|bash' and 'echo "root:fJOKRFQ0oaGB"|chpasswd|bash' result in 'echo "root:"|chpasswd|bash'
        str_out = buf.getvalue()
        return True, buf.getvalue()
    elif score > 25:
        return True, a
    else:
        return False, ''


def sankey_plot_inputs(file_path):
    session_inputs = {}
    with open(file_path, 'rt') as f:
        for line in f:
            js = orjson.loads(line)

            if js.get('eventid') == 'cowrie.command.input':
                add_to_dictionary(session_inputs, js.get('session'), (js.get('input'), js.get('timestamp')))

    known_commands = []
    for lst in session_inputs.values():
        sessions = len(lst)
        for i in range(sessions):
            input, timestamp = lst[i]
            for c in known_commands:
                if c[0] == input[0]:
                    # possibly same commands
                    probably_same, str_out = similar(input, c)
                    if probably_same:
                        lst[i] = (str_out, timestamp)
                        if str_out not in known_commands:
                            known_commands.append(str_out)

            if input not in known_commands:
                known_commands.append(input)

    source_target_value = {}
    for lst in session_inputs.values():
        num_commands = len(lst)
        for i in range(num_commands):
            input, timestamp = lst[i]

            if i == 0:
                key = (input, 'None')
            if i + 1 < num_commands:
                input_next, timestamp_next = lst[i + 1]
                key = (input, input_next)

            if key in source_target_value:
                source_target_value[key] += 1
            else:
                source_target_value[key] = 1

    sorted_list = sorted(source_target_value.items(), key=operator.itemgetter(1), reverse=True)

    labels = []
    sources = []
    targets = []
    values = []
    feeder = []

    for key, value in sorted_list:
        source_cmd, target_cmd = key
        val = value

        splitter = ''
        if '&&' in source_cmd or '&&' in target_cmd:
            splitter = '&&'
        elif '||' in source_cmd or '||' in target_cmd:
            splitter= '||'

        if splitter == '':
            # normal case
            if source_cmd not in feeder:
                feeder.append(source_cmd)
            if target_cmd not in feeder:
                feeder.append(target_cmd)

            labels.append(f'{source_cmd} : {val}')
            sources.append(feeder.index(source_cmd))
            targets.append(feeder.index(target_cmd))
            values.append(val)
        else:
            # split command case
            src_lst = source_cmd.split(splitter)
            trg_lst = target_cmd.split(splitter)

            total = src_lst + trg_lst

            for i in range(len(total) - 1):
                src_ = total[i]
                trg_ = total[i + 1]

                if src_ not in feeder:
                    feeder.append(src_)
                if trg_ not in feeder:
                    feeder.append(trg_)

                labels.append(f'{src_} : {val}')
                sources.append(feeder.index(src_))
                targets.append(feeder.index(trg_))
                values.append(val)


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
    # session_id = sys.argv[2]

    # print_session_trace(filename, session_id)
    # print_ip_many_session_trace(filename, session_id)
    sankey_plot_inputs(filename)
