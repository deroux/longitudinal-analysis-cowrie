from statistics import mean

import plotly.graph_objects as go
import sys
import json

# changes week
# changes month
# changes 6 months

# Date-Range angeben
# Vertical Table
# Date | Password | % Overall | % Increase
from Helpers import add_to_dictionary, key_exists


def build_statistics_figures(d, text, threshold, figure_list):
    fig_1 = create_statistics_table(d, threshold, 1, f'% {text} increase day to previous day')
    fig_7 = create_statistics_table(d, threshold, 7, f'% {text} increase current day over past 7 days mean')
    fig_30 = create_statistics_table(d, threshold, 30, f'% {text} increase current day over past 30 days mean')

    figure_list.append(fig_1)
    figure_list.append(fig_7)
    figure_list.append(fig_30)

def create_statistics_table(events_dict, threshold, compare_day, title):
    events = []
    dates = []
    counts = []

    perc_overall = []
    perc_increase = []

    overall_dict = {}

    for obj in events_dict.keys():
        ht = obj.split(':')
        # honeypot = ht[0]
        event = ht[1] + ':' + ht[2]
        if ht[2] == '':
            event = ht[1]

        honeypot_counts = events_dict[obj]

        for count in honeypot_counts:
            sp = count.split(':')

            date = sp[0]
            count = int(sp[1])

            dates.append(date)
            events.append(event)
            counts.append(count)

            add_to_dictionary(overall_dict, f'{event}', count)

    for i in range(len(events)):
        total = sum(overall_dict[events[i]])
        a = int(counts[i])
        overall = (100 / total) * a
        perc_overall.append(overall)

    # change to 7::1 for changes over 7 days
    if compare_day == 1:
        for a, b in zip(counts[::1], counts[compare_day::1]):
            percent = 100 * (a - b) / b
            perc_increase.append(percent)
    else:
        n = compare_day
        mean_list = []
        for el in counts:
            idx = counts.index(el)
            list_of_counts = counts[idx:n]

            if len(list_of_counts) == 0:
                continue

            mean_list.append(mean(list_of_counts))
            n += 1

        for a, b in zip(counts[::1], mean_list[::1]):
            percent = 100 * (a - b) / b
            perc_increase.append(percent)


    thresh = threshold # float

    k = 0
    for el in perc_increase.copy():
        if abs(el) > thresh:
            k += 1
        else:
            dates.pop(k)
            events.pop(k)
            counts.pop(k)
            perc_overall.pop(k)
            perc_increase.pop(k)

    fig = go.Figure(data=[go.Table(header=dict(values=['Date', 'Event', 'Counts', '% Overall', '% Increase']),
                                   cells=dict(values=[dates, events, counts, perc_overall, perc_increase]))])
    fig.update_layout(title_text=title, title_x=0.5)
    return fig

if __name__ == '__main__':
    # !/usr/bin/env python3
    file = sys.argv[1]
    output_html = sys.argv[2]

    f = open(file, 'r')
    data = json.load(f)

    db = sorted(data, key=lambda k: k['date'], reverse=True)

    pass_dict = {}
    commands_dict = {}
    pre_disc_comm_dict = {}
    connect_dict = {}
    sessionclosed_dict = {}
    download_dict = {}
    upload_dict = {}
    proxy_request_dict = {}

    for obj in db:
        honeypot = obj['sensor']
        date = obj ['date']

        passwords = obj['passwords']
        commands = obj.get('commands')
        pre_disconnect_commands = obj.get('pre_disconnect_command')
        connects = obj.get('connect')
        session_closed = obj['session_closed']
        file_download = obj.get('file_download')
        file_upload = obj.get('file_upload')
        proxy_request = obj.get('proxy_request')

        for el in passwords:
            user = el['username']
            pas = el['password']
            count = int(el['count'])
            add_to_dictionary(pass_dict, f'{honeypot}:{user}:{pas}', f'{date}:{count}')

        if key_exists(obj, 'commands'):
            for el in commands:
                inp = el['input']
                count = int(el['count'])
                add_to_dictionary(commands_dict, f'{honeypot}:{inp}:', f'{date}:{count}')

        if key_exists(obj, 'pre_disconnect_command'):
            for el in pre_disconnect_commands:
                inp = el['input']
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
                add_to_dictionary(sessionclosed_dict, f'{honeypot}:{src_ip}:{robot}', f'{date}:{count}')

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
                add_to_dictionary(proxy_request_dict, f'{honeypot}:{src_ip}:{filename}', f'{date}:{count}')



    threshold = 20.0
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
    d = sessionclosed_dict
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