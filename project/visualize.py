import json, sys
import plotly.graph_objects as go
import os

from Helpers import add_to_dictionary, key_exists, key_exists_arr


# todo: integrate animated bubble_chart

def histogram(data, title):
    fig = go.Figure()

    for key in data:
        x_data = []
        y_data = []
        z_data = []

        elements = data[key]
        # shorten text key (as long commands might destroy layout)
        key = (key[:75] + '..') if len(key) > 75 else key

        for el in elements:
            spl = el.split(':')
            date = spl[0]  # + ':' + spl[1]
            sensor = spl[1]
            count = int(spl[2])

            for i in range(count):
                x_data.append(date)
            y_data.append(count)
            z_data.append(sensor)

        fig.add_trace(go.Histogram(
            x=x_data,
            name=key, text=[key + ':' + str(x) for x in x_data]))

    fig.update_xaxes(title_text='date')
    fig.update_yaxes(title_text='count')
    # Overlay both histograms
    fig.update_layout(title=f"{title}", barmode='overlay')
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.75)
    return fig


def line_chart(data, str_xaxis, str_yaxis, str_zaxis, title, legend_title):
    import numpy as np

    fig_2d = go.Figure()

    for key in data:
        x_data = []
        y_data = []
        z_data = []

        elements = data[key]
        # shorten text key (as long commands might destroy layout)
        key = (key[:75] + '..') if len(key) > 75 else key

        for el in elements:
            spl = el.split(':')
            date = spl[0]  # + ':' + spl[1]
            # sensor = spl[1]
            count = int(spl[2])
            x_data.append(date)
            y_data.append(count)
            # z_data.append(sensor)


        fig_2d.add_trace(go.Scatter(
            x=x_data, y=y_data,
            name=key, text=[key + ':' + str(y) for y in y_data],
            mode='lines+markers',
            connectgaps=False,
            line_shape='linear' # 'spline' or 'linear' 'hv'
            # marker_size=m_size
        ))  # , row=2, col=1)
        fig_2d.update_xaxes(title_text=str_xaxis)
        fig_2d.update_yaxes(title_text=str_yaxis, type="log")
        fig_2d.update_layout(title=f"{title}",
                             legend_title=f"{legend_title}",
                             font=dict(
                                 family="Courier New, monospace",
                                 size=14,
                                 color="Black"
                             ))

    return fig_2d


def bubble_chart(data, str_xaxis, str_yaxis, str_zaxis, title, legend_title):
    fig_2d = go.Figure()
    data_3d = []

    for key in data:
        x_data = []
        y_data = []
        z_data = []

        elements = data[key]
        # shorten text key (as long commands might destroy layout)
        key = (key[:75] + '..') if len(key) > 75 else key

        for el in elements:
            spl = el.split(':')
            date = spl[0]  # + ':' + spl[1]
            sensor = spl[1]
            count = int(spl[2])
            x_data.append(date)
            y_data.append(count)
            z_data.append(sensor)

        # normalize y data to build marker size
        m_size = normalize_range(y_data, max(y_data), min(y_data), 100, 10)
        fig_2d.add_trace(go.Scatter(
            x=x_data, y=y_data,
            name=key, text=[key + ':' + str(y) for y in y_data],
            mode='markers',
            marker_size=m_size
        ))  # , row=2, col=1)
        fig_2d.update_xaxes(title_text=str_xaxis)
        fig_2d.update_yaxes(title_text=str_yaxis, type="log")
        fig_2d.update_layout(title=f"{title}",
                             legend_title=f"{legend_title}",
                             font=dict(
                                 family="Courier New, monospace",
                                 size=14,
                                 color="Black"
                             ))

        data_3d.append(go.Scatter3d(
            x=x_data,
            y=y_data,
            z=z_data,
            text=key,
            name=key,
            showlegend=True,
            mode='markers',
            marker=dict(
                sizemode='diameter',
                # sizeref=100,
                size=m_size,
                opacity=0.8,
                line_color='rgb(140, 140, 170)'
            )))

    # fig.show()
    # layout = dict(updatemenus=updatemenus, title='Linear scale')
    layout_3d = {
        "scene": {
            "xaxis": {
                "title": f"{str_xaxis}"
            },
            "yaxis": {
                "type": "log",
                "title": f"{str_yaxis}"
            },
            "zaxis": {
                "title": f"{str_zaxis}"
            },
        },
        "title": f"{title}",
        "legend_title": f"{legend_title}",
        "font": {
            "family": "Courier New, monospace",
            "size": 14,
            "color": "Black"
        },
        "hovermode": "closest",
        "showlegend": True
    }
    fig_3d = go.Figure(data=data_3d, layout=layout_3d)

    return fig_2d, fig_3d


def normalize_range(data, OldMax, OldMin, NewMax, NewMin):
    # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    OldRange = (OldMax - OldMin)
    normalized = []
    for el in data:
        if OldRange == 0:
            NewValue = NewMin
        else:
            NewRange = (NewMax - NewMin)
            NewValue = (((el - OldMin) * NewRange) / OldRange) + NewMin
        normalized.append(round(NewValue, 0))  # rounded to e.g. 5.35453 => 5
    return normalized;


if __name__ == '__main__':
    # !/usr/bin/env python3
    if len(sys.argv) > 1:
        reduced_json = sys.argv[1]
    if len(sys.argv) == 3:
        output_html = sys.argv[2]
    else:
        output_html = 'result.html'

    try:
        f = open(reduced_json, 'r')
        db = json.load(f)

        # sort by date
        lines = sorted(db, key=lambda k: k['date'], reverse=False)

        userpw_dict = {}
        commands_dict = {}
        pre_disconnect_commands_dict = {}
        connect_dict = {}
        sessionclosed_dict = {}
        download_dict = {}
        upload_dict = {}
        proxy_request_dict = {}

        passwords_dict = {}

        dates = []
        sensors = []
        pws = []
        counts = []

        downloads = {}
        downloads_y_global = []
        uploads_y_global = []

        for entry in lines:
            date = key_exists_arr(entry, 'date')
            sensor = key_exists_arr(entry, 'sensor')
            passwords = key_exists_arr(entry, 'passwords')
            commands = key_exists_arr(entry, 'commands')
            pre_disconnect_command = key_exists_arr(entry, 'pre_disconnect_command')
            connect = key_exists_arr(entry, 'connect')
            session_closed = key_exists_arr(entry, 'session_closed')
            file_download = key_exists_arr(entry, 'file_download')
            file_upload = key_exists_arr(entry, 'file_upload')
            proxy_request = key_exists_arr(entry, 'proxy_request')

            if key_exists(entry, 'file_download'):
                for el in entry['file_download']:
                    url = el['url']

                    if url == '' or url == None:
                        continue

                    outfile = el['outfile']
                    avira = f"{el['scans']['positives']} / {el['scans']['total']} positives."
                    count = el['count']

                    add_to_dictionary(download_dict, url + ' : ' + avira, date + ':' + sensor + ":" + str(count))

            if key_exists(entry, 'file_upload'):
                for el in entry['file_upload']:
                    filename = el['filename']
                    src_ip = el['src_ip']
                    count = el['count']

                    add_to_dictionary(upload_dict, filename + ' : ' + src_ip, date + ':' + sensor + ":" + str(count))

            for el in passwords:
                userpw = el['username'] + ':' + el['password']
                count = el['count']

                add_to_dictionary(userpw_dict, userpw, date + ':' + sensor + ":" + str(count))

            for el in commands:
                inp = el['input']
                count = el['count']

                add_to_dictionary(commands_dict, inp, date + ':' + sensor + ":" + str(count))

            for el in pre_disconnect_command:
                inp = el['input']
                count = el['count']

                add_to_dictionary(pre_disconnect_commands_dict, inp, date + ':' + sensor + ":" + str(count))

            for el in connect:
                src_ip = el['src_ip']
                dst_port = el['dst_port']
                count = el['count']

                add_to_dictionary(connect_dict, f"{src_ip}:{dst_port}", date + ':' + sensor + ":" + str(count))

            for el in session_closed:
                src_ip = el['src_ip']
                robot = el['robot']
                count = int(el['count'])

                add_to_dictionary(sessionclosed_dict, f"{src_ip}:{robot}", date + ':' + sensor + ":" + str(count))

            for el in file_download:
                url = el['url']
                count = int(el['count'])
                pos = el['scans']['positives']
                total = el['scans']['total']

                add_to_dictionary(download_dict, f"{url} : {pos} / {total}", date + ':' + sensor + ":" + str(count))

            for el in file_upload:
                filename = el['filename']
                src_ip = el['src_ip']
                count = int(el['count'])

                add_to_dictionary(sessionclosed_dict, f"{filename}:{src_ip}", date + ':' + sensor + ":" + str(count))

            for el in proxy_request:
                src_ip = el['src_ip']
                dst_ip = el['dst_ip']
                dst_port = el['dst_port']
                count = int(el['count'])

                add_to_dictionary(proxy_request_dict, f"{src_ip}:{dst_ip}:{dst_port}", date + ':' + sensor + ":" + str(count))

        """
        Future: animated bubblechart for different dates
        
        print(dates)
        df = pd.DataFrame({"Date":dates,
                          "Honeypot":sensors, "Passwords": pws, "Count":counts})
        
        df.set_index('Date', inplace=True)
        df.index = pd.to_datetime(df.index)
        
        figure = bubbleplot(dataset=df, x_column='Count', y_column='Honeypot',
            bubble_column='Passwords', time_column='Date', size_column='Count', color_column='Passwords',
            x_title="Number of logins", y_title="Honeypot", title='Top n logins',
            x_logscale=True, scale_bubble=3, height=650)
        
        # iplot(figure, config={'scrollzoom': True})
        """

        fig_userpw_2d, fig_userpw_3d = bubble_chart(userpw_dict, "date", "log(#logins)", "Droplet",
                                                    "Top n user:password combinations", "user:password")
        fig_userpw_line_2d = line_chart(userpw_dict, "date", "log(#logins)", "Droplet",
                                                    "Top n user:password combinations", "user:password")

        fig_input_2d, fig_input_3d = bubble_chart(commands_dict, "date", "log(#inputs)", "Droplet",
                                                  "Top n commands", "Command")
        fig_input_line_2d = line_chart(commands_dict, "date", "log(#inputs)", "Droplet",
                                                  "Top n commands", "Command")

        fig_pre_disconnect_input_2d, fig_pre_disconnect_input_3d = bubble_chart(pre_disconnect_commands_dict,
                                                                                "date",
                                                                                "log(#inputs)", "Droplet",
                                                                                "Top n pre-disconnect-commands",
                                                                                "Pre-disconnect command")
        fig_pre_disconnect_input_line_2d = line_chart(pre_disconnect_commands_dict,
                                                                                "date",
                                                                                "log(#inputs)", "Droplet",
                                                                                "Top n pre-disconnect-commands",
                                                                                "Pre-disconnect command")

        fig_connect_2d, fig_connect_3d = bubble_chart(connect_dict, "date", "log(#inputs)", "Droplet",
                                                      "Top n connects", "src_ip:dst_port")
        fig_connect_line_2d = line_chart(connect_dict, "date", "log(#inputs)", "Droplet",
                                                      "Top n connects", "src_ip:dst_port")

        fig_histogram_connect = histogram(connect_dict, "Connection frequency")
        fig_histogram_pdc = histogram(pre_disconnect_commands_dict, "Pre disconnect command frequency")

        fig_download_2d, fig_download_3d = bubble_chart(download_dict, "date", "log(#downloads)", "Droplet",
                                                        "Top n downloads", "File : Anti-Virus-Results")
        fig_download_line_2d = line_chart(download_dict, "date", "log(#downloads)", "Droplet",
                                                        "Top n downloads", "File : Anti-Virus-Results")

        fig_upload_2d, fig_upload_3d = bubble_chart(upload_dict, "date", "log(#uploads)", "Droplet",
                                                    "Top n uploads", "filename : src_ip")
        fig_upload_line_2d = line_chart(upload_dict, "date", "log(#uploads)", "Droplet",
                                                    "Top n uploads", "filename : src_ip")

        fig_sc_2d, fig_sc_3d = bubble_chart(sessionclosed_dict, "date", "log(#sessions)", "Droplet",
                                                        "Top n session closed", "src_ip : robot")
        fig_sc_line_2d = line_chart(sessionclosed_dict, "date", "log(#sessions)", "Droplet",
                                                        "Top n session closed", "src_ip : robot")

        fig_proxy_req_2d, fig_proxy_req_3d = bubble_chart(proxy_request_dict, "date", "log(#proxy-requests)", "Droplet",
                                                        "Top n proxy requests", "src_ip : dst_ip : dst_port")
        fig_proxy_line_2d = line_chart(proxy_request_dict, "date", "log(#proxy-requests)", "Droplet",
                                                        "Top n proxy requests", "src_ip : dst_ip : dst_port")

        figure_list = [
            fig_userpw_line_2d, fig_userpw_3d,
            fig_input_line_2d, fig_input_3d,
            fig_pre_disconnect_input_line_2d, fig_pre_disconnect_input_3d,
            fig_histogram_pdc,
            fig_connect_line_2d, fig_connect_3d,
            fig_histogram_connect,
            fig_download_line_2d, fig_download_3d,
            fig_upload_line_2d, fig_upload_3d,
            fig_sc_line_2d, fig_sc_3d,
            fig_proxy_line_2d, fig_proxy_req_3d
        ]

        """
        """

        file_count = 0
        no_extension = str(output_html).rsplit('.', 1)[0]

        while len(figure_list) > 1:
            file = f'{no_extension}-{file_count}.html'
            with open(file, 'w') as f:  # a for append
                too_big = 5*1024**2 # 5 MB is considered too big
                run = True
                while run:
                    fig = figure_list.pop(0)
                    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                    size = os.path.getsize(f.name)

                    if size > too_big:
                        run = False

                print(f'created {file}')
            file_count += 1
    except Exception as e:
        print(e)
        exit(0)