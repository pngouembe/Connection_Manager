#!/usr/bin/env python3

import os
import socket
import threading 
import time
import sys
import argparse

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
    while True:
        data = client.recv(1024)
        if not data:
            break
        time.sleep(10)
        client.sendall(data)
    client.close()

def launchServer(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(2)
    i = 0
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
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