#!/usr/bin/env python3

import os
import socket
import sys
sys.path.append('../modules')
from display import Logger, LoggerMgr
import argparse
import time
import threading
import signal

log_mgr = LoggerMgr()
log_mgr.launch_logger_mgr()
Log = log_mgr.Loggers[0]

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
    Log.log(Log.warn_level, "Timeout reached, stoping the client")
    raise KeyboardInterrupt

def launchClient(host, port, cmd, Log, timeout):
    if timeout != 0:
        Log.log(Log.info_level, "Timeout in {} seconds, setting an alarm".format(timeout))
        signal.signal(signal.SIGALRM, stop_client)
        signal.alarm(timeout)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

    Log.log(Log.info_level, "Received: {}".format(repr(data)))
    if cmd != '':
        Log.log(Log.info_level, "Launching cmd : {}".format(cmd))
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
    Log.log(Log.info_level, "Received".format(repr(data)))
    s.close()

def main(argv):
    parser = setup_argument_parser()
    host, port, cmd, timeout = get_arguments(parser)

    Log.log(Log.info_level, "launching connection manager") 

    launchClient(host, port, cmd, Log, timeout)
    Log.log(Log.info_level, "client exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()

if __name__ == "__main__":
    main(sys.argv[1:])