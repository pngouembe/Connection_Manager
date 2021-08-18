#!/usr/bin/env python3

import os
import socket
import threading 
import time
import sys
import argparse

lock = threading.Lock()
connection_list = []
connection_number = 0
active_connection = 0
server_running = False

def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Server-side connection manager',\
                                     usage='python3 Connection_manager_server.py -a <IP address> -p <Port>',\
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-a', '--address', default='localhost', metavar='', help='the machine\'s IP address')
    parser.add_argument('-p', '--port', type=int, default=65432, metavar='', help='port used for the connection')
    
    return parser

def get_arguments(parser):
    args = parser.parse_args()
    return args.address, args.port

def client_handler(client, addr):
    global connection_list
    global connection_number
    global active_connection

    client_data = (connection_number, client, addr)

    lock.acquire()
    connection_list.append(client_data)
    connection_number += 1
    active_connection += 1
    lock.release()

    while True:
        data = client.recv(1024)
        if not data:
            break
        elif data == b"END_CONNECTION":
            client.sendall(b"Connection ended per client request")
            break
        client.sendall(data)
    client.close()

    lock.acquire()
    connection_list.remove(client_data)
    active_connection -= 1
    lock.release()

def server_log():
    global connection_list
    global active_connection

    while server_running == True:

        lock.acquire()
        print("Connection list:")
        print(connection_list)
        print("\n\nActive connections: {}\n\n".format(active_connection))
        lock.release()
        time.sleep(3)
    

def launchServer(host, port):
    global server_running
    lock.acquire()
    server_running = True
    lock.release()

    log_thread = threading.Thread(target=server_log)
    log_thread.start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(2)
    i = 0
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            lock.acquire()
            server_running = False
            lock.release()
            break
        print('Connected by', addr)
        t = threading.Thread(target=client_handler, args=(conn, addr))
        t.start()

    t.join()
    s.close()

def main(argv):
    parser = setup_argument_parser()
    host, port = get_arguments(parser)

    print("launching connection manager")    
    launchServer(host, port)
    print ("server exit")
    

if __name__ == "__main__":
    main(sys.argv[1:])