#! /usr/bin/python3 

import socket
import threading
import sys
import argparse
from datetime import datetime



IP = '0.0.0.0'
PORT = 8888


class Chat_Server:

    def __init__(self):
        self.sockets_list = {}
        self.recipient = ''

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((IP, PORT))
        self.server.listen(10)
        print(f"[+] Listening on {IP}:{PORT}")

        try:
            while True:
                client_socket, client_address = self.server.accept()
                self.sockets_list.update( {client_socket: ''} )
                print(f"[*] Accept connection from {client_address[0]}:{client_address[1]}")

                thread = threading.Thread(target=self.receive_message, args=(client_socket,))
                thread.daemon = True
                thread.start()

        except Exception as e:
            print(f"[!] Error: {e}")
            for cs in self.sockets_list.keys():
                if cs.fileno() == -1:
                    cs.close()
            # sys.exit(1)



    def receive_message(self, client_socket):

        try:
            while True:
                recv_len = 1
                response = b""

                while recv_len:
                    data = client_socket.recv(4096)
                    recv_len = len(data)
                    response += data

                    if recv_len < 4096:
                        break
                
                # Set socket's associated username
                self.update_username(client_socket, response)


                # Send received message to users
                date = datetime.now().strftime('%Y-%m-')

                if date.encode('utf-8') in response:

                    for cs in self.sockets_list.keys():
                        if cs == client_socket:
                            # Log for server
                            data = f"[LOG:{self.sockets_list.get(cs)}] => {response.decode('utf-8')}"
                            print(data)

                        else:
                            cs.send(response)

                # Send the received file content to the specified users
                elif b"FILE" in response:
                    decoded_response = response.decode('utf-8')
                    data = f"[LOG:{self.sockets_list.get(client_socket)}] => {decoded_response}"
                    print(data)

                    splitted_response = decoded_response.split()
                    filename, self.recipient = splitted_response[1], splitted_response[2]
                    filename = filename.rsplit('/')[-1]

                    data = f'FILE {filename}'.encode('utf-8')
                    self.send_to(self.recipient, data)
            
                elif len(response):
                    print('[+] File received')
                    self.send_to(self.recipient, response)
                    
                
        except Exception as e:
            print(f'[!] Error(server): {e}')


    def send_to(self, u, d):
        for sock, user in self.sockets_list.items():
            if u == user:
                sock.send(d)


    def update_username(self, client_socket, response):
        if self.sockets_list.get(client_socket) == '':
            username = response.decode('utf-8').split()[2].replace(':', '')
            self.sockets_list.update({client_socket: username})



def main():

    global IP, PORT

    ag = argparse.ArgumentParser(description="server.py arguments")
    ag.add_argument('--ip', help="IP address to bind", type=str)
    ag.add_argument('--port', '-p', help="Port number to bind", type=int)
    args = ag.parse_args()

    try:
        if args.ip:
            IP = args.ip 
        if args.port:
            PORT = args.port

        Chat_Server()

    except Exception as e:
        print(f'[!] Error: {e}')
        sys.exit(1)



if __name__ == "__main__":
    main()
