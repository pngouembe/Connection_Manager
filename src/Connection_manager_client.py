#!/usr/bin/env python3

import os
import socket
import sys
import argparse
import time
import threading
import signal

def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Client-side connection manager',\
                                     usage='python3 Connection_manager_client.py -a <IP address> -p <Port> -c \'<Command>\'',\
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-a', '--address', default='localhost', metavar='', help='the machine\'s IP address')
    parser.add_argument('-p', '--port', type=int, default=65432, metavar='', help='port used for the connection')
    parser.add_argument('-c', '--cmd', default='', metavar='', help='command used for the connection')
    parser.add_argument('-t', '--timeout', type=int, default=0, metavar='', help='timespan before client automatically ends the connection (in sec)')
    
    return parser

def get_arguments(parser):
    args = parser.parse_args()
    return args.address, args.port, args.cmd, args.timeout

def stop_client(*args):
    raise KeyboardInterrupt

def launchClient(host, port, cmd, timeout):
    if timeout != 0:
        print("hello")
        signal.signal(signal.SIGALRM, stop_client)
        signal.alarm(timeout)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

    print('Received', repr(data))
    if cmd != '':
        print("Launching cmd : {}".format(cmd))
        os.system(cmd)
    else:
        while True:
            try:
                signal.pause()
            except KeyboardInterrupt:
                break

    # Handling socket closure                
    s.sendall(b"END_CONNECTION")
    data = s.recv(1024)
    print('Received', repr(data))
    s.close()

def main(argv):
    parser = setup_argument_parser()
    host, port, cmd, timeout = get_arguments(parser)
    
    print("launching connection manager")

    launchClient(host, port, cmd, timeout)
    print ("client exit")

if __name__ == "__main__":
    main(sys.argv[1:])