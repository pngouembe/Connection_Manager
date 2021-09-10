#!/usr/bin/env python3

import json
import socket
import threading 
import time
import sys
sys.path.append('../modules')
from display import Logger, LoggerMgr
import argparse
from json import loads

log_mgr = LoggerMgr()
log_mgr.launch_logger_mgr()
Log = log_mgr.Loggers[0]

c_list_lock = threading.Lock()
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

def client_handler(client, addr, Log:Logger):
    global connection_list
    global connection_number
    global active_connection

    client_data = [connection_number, *addr, "DUMMY NAME"]

    c_list_lock.acquire()
    connection_list.append(client_data)
    connection_number += 1
    active_connection += 1
    c_list_lock.release()

    while True:
        data = client.recv(1024)
        if not data:
            break
        else:
            try:
                msg_header, payload = data.decode().split("|||")
            except ValueError:
                #TODO deal with bad message format
                pass
            if msg_header == "INTRODUCE":
                tmp = json.loads(payload)
            elif data == b"END_CONNECTION":
                client.sendall(b"Connection ended per client request")
                break
        Log.log(Log.dbg_level, "new client accepted : {}".format(tmp["name"]))
        client.sendall(b"ACK")
        Log.log(Log.dbg_level, "ACK sent")
    client.close()

    c_list_lock.acquire()
    connection_list.remove(client_data)
    active_connection -= 1
    c_list_lock.release()
    Log.log(Log.info_level, "Client #{} disconnected".format(client_data[0]))
    

def launchServer(host, port, Log):
    global server_running
    c_list_lock.acquire()
    server_running = True
    c_list_lock.release()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bound = False
    while not bound:
        try:
            s.bind((host, port))
            bound = True
            Log.log(Log.info_level, "bind successful")
        except OSError:
            Log.log(Log.err_level, "Failed to bind, trying again in 5 seconds...")
            time.sleep(5)
    s.listen(2)
    i = 0
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            c_list_lock.acquire()
            server_running = False
            c_list_lock.release()
            break
        #print('Connected by', addr)
        t = threading.Thread(target=client_handler, args=(conn, addr, Log))
        t.start()

    t.join()
    s.close()

def main(argv):
    parser = setup_argument_parser()
    host, port = get_arguments(parser)

    Log.log(Log.info_level, "launching connection manager")    
    launchServer(host, port, Log)
    Log.log(Log.info_level, "server exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()

if __name__ == "__main__":
    main(sys.argv[1:])