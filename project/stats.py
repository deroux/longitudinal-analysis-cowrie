from statistics import mean

import plotly.graph_objects as go
import sys
import json

# changes week
# changes month
# changes 6 months

# provide Date-Range
# Vertical Table
# Date | Password | % Overall | % Increase
from Helpers import add_to_dictionary, key_exists


def build_statistics_figures(dic, event, thresh, fig_list):
    fig_1 = create_statistics_table(dic, thresh, 1, f'% {event} increase day to previous day')
    fig_7 = create_statistics_table(dic, thresh, 7, f'% {event} increase current day over past 7 days mean')
    fig_30 = create_statistics_table(dic, thresh, 30, f'% {event} increase current day over past 30 days mean')

    fig_list.append(fig_1)
    fig_list.append(fig_7)
    fig_list.append(fig_30)
    return fig_list


def create_statistics_table(events_dict, thresh, compare_day, title):
    events = []
    dates = []
    counts = []

    percent_overall = []
    percent_increase = []

    overall_dict = {}

    for item in events_dict.keys():
        ht = item.split(':')
        # honeypot = ht[0]
        event = ht[1] + ':' + ht[2]
        if ht[2] == '':
            event = ht[1]

        honeypot_counts = events_dict[item]

        for elem in honeypot_counts:
            sp = elem.split(':')

            e_date = sp[0]
            e_count = int(sp[1])

            dates.append(e_date)
            events.append(event)
            counts.append(e_count)

            add_to_dictionary(overall_dict, f'{event}', count)

    for i in range(len(events)):
        total = sum(overall_dict[events[i]])
        a = int(counts[i])
        overall = (100 / total) * a
        percent_overall.append(overall)

    # change to 7::1 for changes over 7 days
    if compare_day == 1:
        for a, b in zip(counts[::1], counts[compare_day::1]):
            percent = 100 * (a - b) / b
            percent_increase.append(percent)
    else:
        n = compare_day
        mean_list = []
        for item in counts:
            idx = counts.index(item)
            list_of_counts = counts[idx:n]

            if len(list_of_counts) == 0:
                continue

            mean_list.append(mean(list_of_counts))
            n += 1

        for a, b in zip(counts[::1], mean_list[::1]):
            percent = 100 * (a - b) / b
            percent_increase.append(percent)

    k = 0
    for item in percent_increase.copy():
        if abs(item) > thresh:
            k += 1
        else:
            dates.pop(k)
            events.pop(k)
            counts.pop(k)
            percent_overall.pop(k)
            percent_increase.pop(k)

    fig = go.Figure(data=[go.Table(header=dict(values=['Date', 'Event', 'Counts', '% Overall', '% Increase']),
                                   cells=dict(values=[dates, events, counts, percent_overall, percent_increase]))])
    fig.update_layout(title_text=title, title_x=0.5)
    return fig


if __name__ == '__main__':
    # !/usr/bin/env python3
    file = sys.argv[1]
    output_html = sys.argv[2]
    threshold = float(sys.argv[3])

    f = open(file, 'r')
    data = json.load(f)

    db = sorted(data, key=lambda k: k['date'], reverse=True)

    pass_dict = {}
    commands_dict = {}
    pre_disc_comm_dict = {}
    connect_dict = {}
    session_closed_dict = {}
    download_dict = {}
    upload_dict = {}
    proxy_request_dict = {}

    for obj in db:
        honeypot = obj['sensor']
        date = obj['date']

        passwords = obj.get('passwords')
        commands = obj.get('commands')
        pre_disconnect_commands = obj.get('pre_disconnect_command')
        connects = obj.get('connect')
        session_closed = obj.get('session_closed')
        file_download = obj.get('file_download')
        file_upload = obj.get('file_upload')
        proxy_request = obj.get('proxy_request')

        if key_exists(obj, 'passwords'):
            for el in passwords:
                user = el['username']
                pas = el['password']
                count = int(el['count'])
                add_to_dictionary(pass_dict, f'{honeypot}:{user}:{pas}', f'{date}:{count}')

        if key_exists(obj, 'commands'):
            for el in commands:
                inp = el['input']
                if len(inp) > 100:
                    inp = inp[0: 50] + '..'
                count = int(el['count'])
                add_to_dictionary(commands_dict, f'{honeypot}:{inp}:', f'{date}:{count}')

        if key_exists(obj, 'pre_disconnect_command'):
            for el in pre_disconnect_commands:
                inp = el['input']
                if len(inp) > 100:
                    inp = inp[0: 50] + '..'
                count = int(el['count'])
                add_to_dictionary(pre_disc_comm_dict, f'{honeypot}:{inp}:', f'{date}:{count}')

        if key_exists(obj, 'connect'):
            for el in connects:
                src_ip = el['src_ip']
                dst_port = el['dst_port']
                count = int(el['count'])
                add_to_dictionary(connect_dict, f'{honeypot}:{src_ip}:{dst_port}', f'{date}:{count}')

        if key_exists(obj, 'session_closed'):
            for el in session_closed:
                src_ip = el['src_ip']
                robot = el['robot']
                count = int(el['count'])
                add_to_dictionary(session_closed_dict, f'{honeypot}:{src_ip}:{robot}', f'{date}:{count}')

        if key_exists(obj, 'file_download'):
            for el in file_download:
                url = el['url']
                count = int(el['count'])
                add_to_dictionary(download_dict, f'{honeypot}:{url}:', f'{date}:{count}')

        if key_exists(obj, 'file_upload'):
            for el in file_upload:
                filename = el['filename']
                src_ip = el['src_ip']
                count = int(el['count'])
                add_to_dictionary(upload_dict, f'{honeypot}:{src_ip}:{filename}', f'{date}:{count}')

        if key_exists(obj, 'proxy_request'):
            for el in proxy_request:
                src_ip = el['src_ip']
                dst_ip = el['dst_ip']
                dst_port = el['dst_port']
                count = int(el['count'])
                add_to_dictionary(proxy_request_dict, f'{honeypot}:{src_ip}:{dst_ip}:{dst_port}', f'{date}:{count}')

    figure_list = []

    # user:password
    d = pass_dict
    text = 'user:password'
    build_statistics_figures(d, text, threshold, figure_list)
    # commands
    d = commands_dict
    text = 'commands'
    build_statistics_figures(d, text, threshold, figure_list)
    # pre_disc_commands
    d = pre_disc_comm_dict
    text = 'pre-disconnect-commands'
    build_statistics_figures(d, text, threshold, figure_list)
    # connects
    d = connect_dict
    text = 'connects'
    build_statistics_figures(d, text, threshold, figure_list)
    # session_closed
    d = session_closed_dict
    text = 'session_closed'
    build_statistics_figures(d, text, threshold, figure_list)
    # file_download
    d = download_dict
    text = 'file_download'
    build_statistics_figures(d, text, threshold, figure_list)
    # file_upload
    d = upload_dict
    text = 'file_upload'
    build_statistics_figures(d, text, threshold, figure_list)
    # proxy_requests
    d = proxy_request_dict
    text = 'proxy_requests'
    build_statistics_figures(d, text, threshold, figure_list)

    with open(output_html, 'w') as f:  # a for append
        for figure in figure_list:
            f.write(figure.to_html(full_html=False, include_plotlyjs='cdn'))
        print(f'created {output_html}')
