#!/usr/bin/env python3

from typing import Tuple
import yaml
import getpass
import time
import argparse
import os
import socket
import sys

sys.path.append('../modules')

# Project modules
from display import Logger, LoggerMgr
from user import User
from com_protocole import ComProtocole, ComHeaders
import client_actions
import global_vars

log_mgr = LoggerMgr()
log_mgr.launch_logger_mgr()
Log: Logger = log_mgr.Loggers[0]

private_info = ["address", "port", "cmd", "cfg_file", "Entity_type"]
default_config_file_name = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    "../config/client_config_template.yml")


def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Client-side connection manager',
                                     usage='python3 Connection_manager_client.py -a <IP address> -p <Port> -c \'<Command>\'',
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-n', '--name', metavar='',
                        help="user's name that will be communicated to the server", required=False)
    parser.add_argument('-a', '--address', default='localhost',
                        metavar='', help='the machine\'s IP address')
    parser.add_argument('-p', '--port', type=int, required=False,
                        metavar='', help='port used for the connection')
    parser.add_argument('-c', '--cmd', required=False, metavar='',
                        help='command used for the connection')
    parser.add_argument('-t', '--timeout', type=int, required=False, metavar='',
                        help='timespan before client automatically ends the connection (in sec)')
    parser.add_argument('-C', '--comment', type=str, required=False,
                        metavar='', help='comment to show to other users')
    parser.add_argument('-r', '--resource', type=int, required=False,
                        metavar='', help='ID of the resource to use')
    parser.add_argument('--cfg_file',
                        type=str,
                        default=default_config_file_name,
                        metavar='',
                        help='path to the config file',
                        required=False)


    return parser


def get_config(parser) -> Tuple[dict, dict]:
    args = parser.parse_args()
    cfg_dict = {}
    if os.path.isfile(args.cfg_file):
        with open(args.cfg_file, "r") as f:
            cfg_dict: dict = yaml.load(f)
        for key, value in vars(args).items():
            if value:
                cfg_dict[key] = value
    else:
        cfg_dict = vars(args)

    print(cfg_dict)
    public_dict = {k: cfg_dict[k] for k in cfg_dict.keys() if k not in private_info}
    private_dict = {k: cfg_dict[k] for k in cfg_dict.keys() if k in private_info}
    return (public_dict, private_dict)


def stop_client(*args):
    Log.log(Log.warn_level, "Timeout reached, stoping the client")
    raise KeyboardInterrupt


def launchClient(user: User) -> None:

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((user.get_user_info("address"), user.get_user_info("port")))

    # dumping user's public info to send them to the server
    payload = user.json_dump()
    msg = ComProtocole.generate_msg(ComHeaders.INTRODUCE, payload)
    Log.log(Log.info_level, "Sending: {}".format(payload))
    s.sendall(msg.encode())

    while user.is_com_active():
        try:
            data = s.recv(1024)
        except KeyboardInterrupt:
            user.desactivate_com()
            break
        if not data:
            break
        else:
            message_list = ComProtocole.decode_msg(data.decode())
            for msg_header, payload in message_list:
                # Calling the action linked to the header received.
                client_actions.action_list[msg_header.value](user, payload)

    # Handling socket closure
    if user.is_timed_out():
        header = ComHeaders.TIMEOUT
    else:
        header = ComHeaders.END_CONNECTION

    s.sendall(ComProtocole.generate_msg(header).encode())
    data = s.recv(1024)
    message_list = ComProtocole.decode_msg(data.decode())
    for msg_header, payload in message_list:
        # Calling the action linked to the header received.
        client_actions.action_list[msg_header.value](user, payload)
    s.close()
    del user


def main(argv):
    parser = setup_argument_parser()
    public_dict, private_dict = get_config(parser)

    # Adding client parameters into user object
    user = User(public_dict)

    user.add_private_info(private_dict)

    # Adding logger to user context
    user.register_logger(Log)

    client_actions.init_action_list()
    global_vars.init()

    Log.log(Log.info_level, "launching connection manager")

    launchClient(user)
    Log.log(Log.info_level, "client exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()


if __name__ == "__main__":
    main(sys.argv[1:])
