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

    import paramiko
    try:
        # fetch reduced.json file
        print(f"Copying reduced JSON from {ip_address}:{port}")
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
    except Exception as e:
        print(f"Error fetching files from remote {ip}:{port}")
        print(e)
        exit(0)


def deploy_to_remote(ip_address, port, user, pw):
    import paramiko
    print(f"Deploying scripts to {ip_address}:{port}")
    try:
        # Connect to remote host
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip_address, username=user, password=pw, port=port)

        commands = []
        # update ubuntu and install required libraries
        commands.append("sudo apt-get -y update && sudo apt-get -y upgrade")
        commands.append("sudo apt-get -y install python3.6")
        commands.append("sudo apt install -y python-pip")
        commands.append("sudo apt install -y python3-pip")
        # create virtual environment
        commands.append("sudo apt-get -y install python3-venv")
        commands.append("python3 -m venv honeypot-env")
        commands.append("source honeypot-env/bin/activate")
        # upgrade pip's
        commands.append("sudo -H pip3 install --upgrade pip")
        # install required libraries
        commands.append("pip3 install paramiko")
        commands.append("pip3 install orjson")
        commands.append("pip3 install psutil")

        for command in commands:
            stdin, stdout, stderr = client.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                print(line, end="")

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

        stdin, stdout, stderr = client.exec_command('python3 /home/cowrie/cowrie/var/log/cowrie/remote.py', get_pty=True)

        for line in iter(stdout.readline, ""):
            print(line, end="")
        client.close()
    except Exception as e:
        print(f"Error deploying files to remote {ip}:{port}")
        print(e)
        exit(0)


if __name__ == '__main__':
    #import paramiko

    if len(sys.argv) > 1:
        try:
            """
            ip = sys.argv[1]
            port = sys.argv[2]
            user = sys.argv[3]
            pw = sys.argv[4]
            """
            ip = "104.248.245.133"
            port = 2112
            user = "root"
            pw = "16Sfl,Rkack"
            """
            ip_address = '104.248.253.81'
            port = 2112
            user = 'root'
            pw = '16Sfl,Rkack'
            """
            # deploy to REMOTE server
            deploy_to_remote(ip, port, user, pw)
            # fetch reduced file from REMOTE server
            fetch_from_remote(ip, port, user, pw)
        except Exception as e:
            print(f"Error executing remote.py script")
            print(e)
            exit(0)
    else:
        # No cmd-line args provided, run script normally (on REMOTE server)
        main()
