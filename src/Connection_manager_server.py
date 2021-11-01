#!/usr/bin/env python3

import argparse
from socket import socket, MSG_DONTWAIT, AF_INET, SOCK_STREAM
import threading
import time
import sys

sys.path.append('../modules')

# Project modules
import global_vars
import server_actions
from com_protocole import ComProtocole, ComHeaders
from user import User
from display import Logger, LoggerMgr

log_mgr = LoggerMgr()
log_mgr.launch_logger_mgr()
Log: Logger = log_mgr.Loggers[0]

c_list_lock = threading.Lock()
connection_list = []
connection_number = 0
active_connection = 0


def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Server-side connection manager',
                                     usage='python3 Connection_manager_server.py -a <IP address> -p <Port>',
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-a', '--address', default='localhost',
                        metavar='', help='the machine\'s IP address')
    parser.add_argument('-p', '--port', type=int, default=65432,
                        metavar='', help='port used for the connection')
    parser.add_argument('-t', '--timeout', type=float, default=0,
                        metavar='', help='Maximum time allowed to a client')

    return parser


def get_arguments(parser):
    args = parser.parse_args()
    return vars(args)


def client_handler(user: User):

    Log: Logger = user.get_logger()
    Log.log(Log.info_level, "Active connections : {}".format(
        user.get_user_count()))
    client: socket = user.get_user_info("socket_obj")
    while user.is_com_active():
        try:
            data = client.recv(1024)
        except ConnectionResetError:
            Log.log(Log.err_level, "Connection to {} lost".format(
                user.get_user_name()))
            break
        if not data:
            break
        else:
            message_list = ComProtocole.decode_msg(data.decode())
            for msg_header, payload in message_list:
                # Calling the action linked to the header received.
                server_actions.action_list[msg_header.value](user, payload)

    client.close()
    if user.is_duplicate():
        Log.log(Log.dbg_level, "Closing {} duplicate".format(
            user.get_user_name()))
    else:
        Log.log(Log.info_level, "{} disconnected".format(user.get_user_name()))
        Log.log(Log.info_level, "Active connections : {}".format(
            user.get_user_count() - 1))
    user.remove_from_list()
    Log.log(Log.dbg_level, "Client list {}".format(user.get_user_names_list()))
    del user


def launchServer(server: User):

    s = socket(AF_INET, SOCK_STREAM)
    bound = False
    while not bound:
        try:
            s.bind((server.get_user_info("host"), server.get_user_info("port")))
            bound = True
            Log.log(Log.info_level, "bind successful")
        except OSError:
            Log.log(Log.err_level, "Failed to bind, trying again in 5 seconds...")
            time.sleep(5)
    s.listen(2)
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            break
        user = User()
        user.add_private_info({"socket_obj": conn, "ip_addr": addr})
        user.register_logger(Log)
        Log.log(Log.info_level, "addr: {}".format(
            user.get_user_info("ip_addr")))
        t = threading.Thread(target=client_handler, args=(user,))
        t.start()
        del user
    try:
        t.join()
    except:
        pass
    s.close()


def main(argv):
    parser = setup_argument_parser()
    server_data = get_arguments(parser)

    server = User(server_data, add_to_list=False)
    server.register_logger(Log)

    server_actions.init_action_list()
    global_vars.init()

    Log.log(Log.info_level, "launching connection manager")
    Log.log(Log.info_level, "Max client timeout : {}s".format(
        server.get_user_info("timeout")))
    global_vars.max_client_execution_time = server.get_user_info("timeout")
    launchServer(server)
    Log.log(Log.info_level, "server exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()


if __name__ == "__main__":
    main(sys.argv[1:])
