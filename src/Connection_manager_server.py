#!/usr/bin/env python3

import json
import socket
import threading 
import time
import sys
sys.path.append('../modules')
from display import Logger, LoggerMgr
from user import User
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

def client_handler(user:User):
    
    if "user_logger" in user.user_info.keys():
        Log = user.user_info["user_logger"]
    Log.log(Log.info_level, "Active connections : {}".format(user.get_user_count()))
    client = user.user_info["client_obj"]
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
                user.update(json.loads(payload))
            elif data == b"END_CONNECTION":
                client.sendall(b"Connection ended per client request")
                break
        Log.log(Log.dbg_level, "new client accepted : {}".format(user.get_user_name()))
        Log.log(Log.dbg_level, "client list : {}".format(user.get_user_names_list()))
        client.sendall(b"ACK")
        Log.log(Log.dbg_level, "ACK sent")
    client.close()

    Log.log(Log.info_level, "Client #{} disconnected".format(user.get_total_user_count()))
    Log.log(Log.info_level, "Active connections : {}".format(user.get_user_count()))
    user.__del__()
    

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
        user = User({"client_obj": conn,"ip_addr":addr, "user_logger":Log})
        t = threading.Thread(target=client_handler, args=(user,))
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