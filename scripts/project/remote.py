import sys
import os

def main():
    stream = open("Map.py")
    map_file = stream.read()
    exec(map_file)

if __name__ == '__main__':
    try:
        if sys.argv[1] == 'deploy':
            import paramiko

            # Connect to remote host
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('104.248.253.81', username='root', password='16Sfl,Rkack', port=2112)

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

            # Setup sftp connection and transmit this script
            sftp = client.open_sftp()
            sftp.put(__file__, '/home/cowrie/cowrie/var/log/cowrie/longitudinal.py')
            sftp.put('Map.py', '/home/cowrie/cowrie/var/log/cowrie/Map.py')
            sftp.put('Helpers.py', '/home/cowrie/cowrie/var/log/cowrie/Helpers.py')
            # sftp.put('config.json', '/home/cowrie/cowrie/var/log/cowrie/config.json')
            sftp.close()

            # Run the transmitted script remotely without args and show its output.
            # SSHClient.exec_command() returns the tuple (stdin,stdout,stderr)
            stdout = client.exec_command('python3 /home/cowrie/cowrie/var/log/cowrie/longitudinal.py')[1]
            for line in stdout:
                # Process each line in the remote output
                print(line)

            client.close()
            sys.exit(0)
    except IndexError:
        pass

    # No cmd-line args provided, run script normally
    main()