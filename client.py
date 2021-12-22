#! /usr/bin/python3

import socket
import threading
import sys
import os
import argparse
import random
from time import sleep
from datetime import datetime

COLORS = [
    "\033[91m__REP__\033[00m", # red
    "\033[92m__REP__\033[00m", # green
    "\033[93m__REP__\033[00m", # yellow
    "\033[95m__REP__\033[00m", # purple
]

IP = ''
PORT = int()
NAME = ''


class Chat_Client:

    def __init__(self):
        self.color = random.choice(COLORS)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"[+] Connecting to {IP}:{PORT}")
        try:
            self.client.connect((IP, PORT))
        except Exception as e:
            print(f"[!] Error: {e}")

        thread = threading.Thread(target=self.receive_message, args=())
        thread.daemon = True
        thread.start()

        while True:
            try:
                i = input()

                if i == "Q":
                    self.client.close()
                    sys.exit(0)
                
                elif "FILE" in i:
                    self.file_handler(i)

                else:
                    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                    date = self.color.replace('__REP__', date)
                    data = f"[{date}] {NAME}: {i}"
                    self.client.send(data.encode('utf-8'))

            except Exception as e:
                print(f"[!] Error: {e}")

    
    def receive_message(self):

        while True:
            recv_len = 1
            response = b""

            while recv_len:
                data = self.client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break
            
            date = datetime.now().strftime('%Y-%m-')
            if date.encode('utf-8') in response:
                print(response.decode('utf-8'))

            elif b'FILE' in response:
                self.filename = response.decode('utf-8').split()[1]
                print(f'[+] File {self.filename} will be received')
            
            elif len(response):
                dir = f'/tmp/chat-server/{NAME}'
                if not os.path.exists(dir):
                    os.mkdir(dir)

                date = datetime.now().strftime('%Y.%m.%d.%H-%M-%S') 
                name, ext = self.filename.rsplit('.', maxsplit=1)
                filename = name + '.' + date + '.' + ext
                f = open(f'{dir}/{filename}', 'wb')
                f.write(response)
                f.close()
                print(f'[+] File {self.filename} successfully saved.')


    
    def file_handler(self, string):
        FORMAT = """# Uploading Format:\n\t`FILE <local_file_path> <recipient_username>`"""
        try:
            splitted_string = string.split()
            if len(splitted_string) != 3:
                print(FORMAT)

            else:
                filename = splitted_string[1]

                try:
                    f = open(filename, 'rb')
                    filename = f.read()
                    self.client.send(string.encode('utf-8'))
                    sleep(1)
                    self.client.sendall(filename)
                    print('[+] File has been sent')
                    f.close()

                except (FileExistsError, FileNotFoundError) as e:
                    print(f'[!]{e}')
                

        except Exception as e:
            print(f'[!] Error(client): {e}')
            sys.exit(1)


def main():
    global IP, PORT, NAME

    ag = argparse.ArgumentParser(description="Client.py arguments")
    ag.add_argument('--name', '-n', help="name of the client", type=str)
    ag.add_argument('--ip', help="IP address of the server", type=str)
    ag.add_argument('--port', '-p', help="Port number of the server", type=int)
    args = ag.parse_args()

    try:
        tmp_dir = '/tmp/chat-server'
        if not os.path.isdir(tmp_dir):
            os.mkdir(tmp_dir)

        IP = args.ip
        PORT = args.port
        NAME = args.name
        Chat_Client()

    except Exception as e:
        print(f'[!] Error: {e}')
        sys.exit(1)



if __name__ == "__main__":
    main()