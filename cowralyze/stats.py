from statistics import mean

import plotly.graph_objects as go
import json
import sys

from Helpers import add_to_dictionary, key_exists


def build_statistics_figures(dic, event, thresh, n, fig_list):
    statistics_figure = create_statistics_table(dic, thresh, n, f'% {event} increase over time across all honeypots (n={n-1}, Thresh={thresh}%)')
    fig_list.append(statistics_figure)
    return fig_list


def create_statistics_table(events_dict, thresh, n, title):
    temp_dict = {}
    for key in events_dict.keys():
        lst = events_dict[key]
        for item in lst:
            s = item.split(':')
            count = s[len(s)-1]
            event = ':'.join(s[1:len(s)-1])
            add_to_dictionary(temp_dict, event, int(count))

    events = []
    event_types = []
    dates = []
    counts = []
    percent_overall = []
    percent_increase = []

    for date in events_dict.keys():
        current_lst = events_dict[date]
        for item in current_lst:
            s = item.split(':')
            count = s[len(s) - 1]
            event_type = s[0]
            event = ':'.join(s[1:len(s) - 1])

            lst_count = temp_dict.get(event)
            a = int(count)
            b = mean(lst_count)

            pct_overall = 100 * (a - b) / b
            pct_overall = float("{:0.2f}".format(pct_overall))

            # 7 days increase
            a = int(count)

            if len(lst_count) == 1:
                n_days = lst_count
            elif len(lst_count) >= n:
                n_days = lst_count[1:n]
            else:
                n_days = lst_count[1:len(lst_count)]

            b = mean(n_days)
            pct_increase = 100 * (a - b) / b
            pct_increase = float("{:0.2f}".format(pct_increase))

            if pct_overall >= thresh and pct_increase >= thresh:
                dates.append(date)
                events.append(event)
                event_types.append(event_type)
                counts.append(count)
                percent_overall.append(pct_overall)
                percent_increase.append(pct_increase)


    fig = go.Figure(data=[go.Table(header=dict(values=['Date', 'Event', 'Command', 'Counts', '% Overall', '% Increase n days']),
                                   cells=dict(values=[dates, event_types, events, counts, percent_overall, percent_increase]))])
    fig.update_layout(title_text=title, title_x=0.5)
    return fig


if __name__ == '__main__':
    # !/usr/bin/env python3
    file = sys.argv[1]
    output_html = sys.argv[2]
    threshold = float(sys.argv[3])
    n = int(sys.argv[4]) + 1 # 7 days >> from 1:8

    f = open(file, 'r')
    data = json.load(f)

    try:
        db = sorted(data, key=lambda k: k['date'], reverse=True)
    except Exception as e:
        print(e)
        db = data

    pass_dict = {}
    commands_dict = {}
    pre_disc_comm_dict = {}
    connect_dict = {}
    session_closed_dict = {}
    download_dict = {}
    upload_dict = {}
    proxy_request_dict = {}

    all = {}

    for obj in db:
        if len(obj) == 0:
            continue
        if type(obj) == list:
            obj = obj[0]

        honeypot = obj['sensor']
        _date = obj['date']

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
                add_to_dictionary(pass_dict, f'{honeypot}:{user}:{pas}', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Login:{user}:{pas}:{count}')

        if key_exists(obj, 'commands'):
            for el in commands:
                inp = el['input']
                if len(inp) > 100:
                    inp = inp[0: 50] + '..'
                count = int(el['count'])
                add_to_dictionary(commands_dict, f'{honeypot}:{inp}:', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Cmd:{inp}:{count}')

        if key_exists(obj, 'pre_disconnect_command'):
            for el in pre_disconnect_commands:
                inp = el['input']
                if len(inp) > 100:
                    inp = inp[0: 50] + '..'
                count = int(el['count'])
                add_to_dictionary(pre_disc_comm_dict, f'{honeypot}:{inp}:', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Pre-disc-cmd:{inp}:{count}')

        if key_exists(obj, 'connect'):
            for el in connects:
                src_ip = el['src_ip']
                dst_port = el['dst_port']
                count = int(el['count'])
                add_to_dictionary(connect_dict, f'{honeypot}:{src_ip}:{dst_port}', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Connect:{src_ip}:{dst_port}:{count}')

        if key_exists(obj, 'session_closed'):
            for el in session_closed:
                src_ip = el['src_ip']
                robot = el['robot']
                count = int(el['count'])
                add_to_dictionary(session_closed_dict, f'{honeypot}:{src_ip}:{robot}', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Sess-closed:{src_ip}:{robot}:{count}')

        if key_exists(obj, 'file_download'):
            for el in file_download:
                url = el['url']
                count = int(el['count'])
                add_to_dictionary(download_dict, f'{honeypot}:{url}:', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Download:{url}:{count}')

        if key_exists(obj, 'file_upload'):
            for el in file_upload:
                filename = el['filename']
                src_ip = el['src_ip']
                count = int(el['count'])
                add_to_dictionary(upload_dict, f'{honeypot}:{src_ip}:{filename}', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Upload:{src_ip}:{filename}:{count}')

        if key_exists(obj, 'proxy_request'):
            for el in proxy_request:
                src_ip = el['src_ip']
                dst_ip = el['dst_ip']
                dst_port = el['dst_port']
                count = int(el['count'])
                add_to_dictionary(proxy_request_dict, f'{honeypot}:{src_ip}:{dst_ip}:{dst_port}', f'{_date}:{count}')
                add_to_dictionary(all, f'{_date}', f'Proxy-request:{src_ip}:{dst_ip}:{dst_port}:{count}')


    figure_list = []
    today = []

    d = all
    text = ''
    build_statistics_figures(d, text, threshold, n, figure_list)

    with open(output_html, 'w') as f:  # a for append
        for figure in figure_list:
            f.write(figure.to_html(full_html=False, include_plotlyjs='cdn'))
        print(f'created {output_html}')
