#!/usr/bin/env python3

import socket
import threading 
import time
import sys
sys.path.append('../modules')
from display import Logger, LoggerMgr
from user import User
from com_protocole import ComProtocole, ComHeaders
from server_actions import *
import argparse

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
    
    Log = user.get_logger()
    Log.log(Log.info_level, "Active connections : {}".format(user.get_user_count()))
    client = user.get_user_info("socket_obj")
    while user.is_com_active():
        data = client.recv(1024)
        if not data:
            break
        else:
            try:
                msg_header, payload = ComProtocole.decode_msg(data.decode())
            except:
                #TODO deal with bad message format
                pass

            # Calling the action linked to the header received.
            action_list[msg_header.value](user, payload)

    client.close()
    user.__del__()

    Log.log(Log.info_level, "Client #{} disconnected".format(user.get_total_user_count()))
    Log.log(Log.info_level, "Active connections : {}".format(user.get_user_count()))
    

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
        user = User({"socket_obj": conn,"ip_addr":addr})
        user.register_logger(Log)
        t = threading.Thread(target=client_handler, args=(user,))
        t.start()

    t.join()
    s.close()

def main(argv):
    parser = setup_argument_parser()
    host, port = get_arguments(parser)

    init_action_list()

    Log.log(Log.info_level, "launching connection manager")    
    launchServer(host, port, Log)
    Log.log(Log.info_level, "server exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()

if __name__ == "__main__":
    main(sys.argv[1:])