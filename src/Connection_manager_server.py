#!/usr/bin/env python3

import argparse
from socket import socket, MSG_DONTWAIT, AF_INET, SOCK_STREAM
import threading
import time
import sys
import os
import yaml

sys.path.append('../modules')

# Project modules
import global_vars
import server_actions
from com_protocole import ComProtocole, ComHeaders
from user import User
from display import Logger, LoggerMgr, WebLogger
from website import create_app

Log: WebLogger = WebLogger()
log_mgr = LoggerMgr(logger_list=[Log])
log_mgr.launch_logger_mgr()
#Log: Logger = log_mgr.Loggers[0]

c_list_lock = threading.Lock()
connection_list = []
connection_number = 0
active_connection = 0

default_config_file_name = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    "../config/server_config_template.yml")
default_resource_file_name = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    "../config/resource_template.yml")


def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Server-side connection manager',
                                     usage='python3 Connection_manager_server.py -a <IP address> -p <Port>',
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-a', '--address',
                        type=str,
                        metavar='',
                        help='the machine\'s IP address',
                        required=False)
    parser.add_argument('-p', '--port',
                        type=int,
                        metavar='',
                        help='port used for the connection',
                        required=False)
    parser.add_argument('--web_port',
                        type=int,
                        metavar='',
                        help='port used for the web server',
                        required=False)
    parser.add_argument('-t', '--timeout',
                        type=float,
                        metavar='',
                        help='Maximum time allowed to a client',
                        required=False
                        )
    parser.add_argument('--cfg_file',
                        type=str,
                        default=default_config_file_name,
                        metavar='',
                        help='path to the config file',
                        required=False)
    parser.add_argument('--rsrc_file',
                        type=str,
                        default=default_resource_file_name,
                        metavar='',
                        help='path to the resource file',
                        required=False)

    return parser


def get_config(parser):
    args = parser.parse_args()
    cfg_dict = {}
    if os.path.isfile(args.cfg_file):
        with open(args.cfg_file, "r") as f:
            cfg_dict: dict = yaml.safe_load(f)
        for key, value in vars(args).items():
            if value:
                cfg_dict[key] = value
    else:
        cfg_dict = vars(args)

    if os.path.isfile(args.rsrc_file):
        with open(args.rsrc_file, "r") as f:
            rsrc_dict: dict = yaml.safe_load(f)
        for key, value in vars(args).items():
            if value:
                rsrc_dict[key] = value
    else:
        rsrc_dict = vars(args)

    cfg_dict.update(rsrc_dict)

    return cfg_dict


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
    Log.log(Log.dbg_level, "Client list : {}".format(
        user.get_user_names_list()))
    del user


def launchServer(server: User):

    s = socket(AF_INET, SOCK_STREAM)
    bound = False
    retries = 0
    max_retries = 0

    # TODO Fix the multiple server launch when max retries > 0
    while not bound:
        try:
            s.bind((server.get_user_info("address"),
                   server.get_user_info("port")))
            bound = True
            Log.log(Log.info_level, "bind successful on {}:{}".format(
                server.get_user_info("address"),
                server.get_user_info("port")))
        except OSError:
            if retries < max_retries :
                Log.log(Log.err_level, "Failed to bind, trying again in 5 seconds...")
                Log.log(Log.err_level, "{}:{}".format(
                    server.get_user_info("address"), server.get_user_info("port")))
                time.sleep(5)
            else:
                exit()
    s.listen(2)
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            break
        user = User()
        user.add_private_info({"socket_obj": conn, "ip_addr": addr})
        user.register_logger(Log)
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
    server_data = get_config(parser)

    server = User(server_data, add_to_list=False)
    server.register_logger(Log)
    if "Resources" in server_data.keys():
        server.init_resources(server_data["Resources"])

    server_actions.init_action_list()
    global_vars.init()

    Log.log(Log.info_level, "launching connection manager")
    if server.get_user_info("timeout"):
        Log.log(Log.info_level, "Max client timeout : {}s".format(
            server.get_user_info("timeout")))
    global_vars.max_client_execution_time = server.get_user_info("timeout")
    global_vars.resource_free_delay = server.get_user_info(
        "resource_free_delay")
    global_vars.reconnexion_retries = server.get_user_info(
        "reconnexion_retries")

    t = threading.Thread(target=launchServer, args=(server,))
    t.start()

    app = create_app()
    app.config['server_data'] = server
    app.run(host=server.get_user_info("address"),
            port=server.get_user_info("web_port"), debug=False)

    t.join()
    Log.log(Log.info_level, "server exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()


if __name__ == "__main__":
    main(sys.argv[1:])
