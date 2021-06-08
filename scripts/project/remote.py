import sys
import os


def main():
    # executed on remote machine

    stream = open("/home/cowrie/cowrie/var/log/cowrie/Map.py")
    map_file = stream.read()
    exec(map_file)

    str = open("/home/cowrie/cowrie/var/log/cowrie/Reduce.py")
    reduce_file = str.read()
    exec(reduce_file)


def error_cli():
    print(f"Please call script like: {sys.argv[0]} IP_ADDRESS PORT USER PASSWORD")
    sys.exit(0)


def fetch_from_remote(ip_address, port, user, pw):
    # fetch reduced.json file
    # Setup sftp connection and fetch the reduced.json file
    remote_path = '/home/cowrie/cowrie/var/log/cowrie/reduced.json'
    local_path = f'C:\\Users\\Dominic\\Documents\\longitudinal-analysis-cowrie\\scripts\\project\\{ip_address}_reduced.json'

    # Connect to remote host
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip_address, username=user, password=pw, port=port)

    sftp = client.open_sftp()
    sftp.get(remote_path, local_path)
    sftp.close()
    print(f'Downloaded reduced log file from {ip_address}:{port} into {local_path}')


def deploy_to_remote(ip_address, port, user, pw):
    try:
        # Connect to remote host
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip_address, username=user, password=pw, port=port)

        """
        stdout = client.exec_command('pip3 install paramiko')[1]
        for line in stdout:
            # Process each line in the remote output
            print(line)

        stdout = client.exec_command('pip3 install psutil')[1]
        for line in stdout:
            # Process each line in the remote output
            print(line)
        # apt install python-pip
        stdout = client.exec_command('apt install python3-pip')[1]
        for line in stdout:
            # Process each line in the remote output
            print(line)
        stdout = client.exec_command('pip3 install --upgrade pip')[1]
        for line in stdout:
            # Process each line in the remote output
            print(line)
        # install orjson
        stdout = client.exec_command('pip3 install orjson')[1]
        for line in stdout:
            # Process each line in the remote output
            print(line)
        stdout = client.exec_command('pip3 install json')[1]
        for line in stdout:
            # Process each line in the remote output
            print(line)
        # /home/cowrie/cowrie/var/log/cowrie
        """
        # Setup sftp connection and transmit this script
        sftp = client.open_sftp()
        print(f"copying {__file__}")
        sftp.put(__file__, '/home/cowrie/cowrie/var/log/cowrie/remote.py')
        print(f"copying Map.py")
        sftp.put('Map.py', '/home/cowrie/cowrie/var/log/cowrie/Map.py')
        print(f"copying Reduce.py")
        sftp.put('Reduce.py', '/home/cowrie/cowrie/var/log/cowrie/Reduce.py')
        print(f"copying Local.py")
        sftp.put('Local.py', '/home/cowrie/cowrie/var/log/cowrie/Local.py')
        print(f"copying Helpers.py")
        sftp.put('Helpers.py', '/home/cowrie/cowrie/var/log/cowrie/Helpers.py')
        print(f"copying MapReduce.py")
        sftp.put('MapReduce.py', '/home/cowrie/cowrie/var/log/cowrie/MapReduce.py')
        print(f"copying config.json")
        sftp.put('config.json', '/home/cowrie/cowrie/var/log/cowrie/config.json')
        sftp.close()

        # Run the transmitted script remotely without args and show its output.
        # SSHClient.exec_command() returns the tuple (stdin,stdout,stderr)

        stdin, stdout, stderr = client.exec_command('python3 /home/cowrie/cowrie/var/log/cowrie/remote.py',
                                                    get_pty=True)
        for line in iter(stdout.readline, ""):
            print(line, end="")

        client.close()
        sys.exit(0)
    except IndexError:
        pass


if __name__ == '__main__':
    import paramiko

    if len(sys.argv) > 1:
        try:
            ip = sys.argv[1]
            port = sys.argv[2]
            user = sys.argv[3]
            pw = sys.argv[4]
            """
            ip_address = '104.248.253.81'
            port = 2112
            user = 'root'
            pw = '16Sfl,Rkack'
            """
            # deploy to REMOTE server
            print(f"Deploying scripts to {ip}:{port}")
            deploy_to_remote(ip, port, user, pw)
            # fetch reduced file from REMOTE server
            print(f"Copying reduced JSON from {ip}:{port}")
            fetch_from_remote(ip, port, user, pw)
        except:
            error_cli()
    else:
        # No cmd-line args provided, run script normally (on REMOTE server)
        main()
