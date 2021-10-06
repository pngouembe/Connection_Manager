#!/usr/bin/env python3

import socket
import sys
from typing import Tuple
sys.path.append('../modules')
from display import LoggerMgr
from user import User
from com_protocole import ComProtocole, ComHeaders
from client_actions import *
import argparse
import time
import signal 
import getpass

log_mgr = LoggerMgr()
log_mgr.launch_logger_mgr()
Log = log_mgr.Loggers[0]

private_info = ["address", "port", "cmd"]

def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Client-side connection manager',\
                                     usage='python3 Connection_manager_client.py -a <IP address> -p <Port> -c \'<Command>\'',\
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-n', '--name', default=getpass.getuser(), metavar='', help="user's name that will be communicated to the server")
    parser.add_argument('-a', '--address', default='localhost', metavar='', help='the machine\'s IP address')
    parser.add_argument('-p', '--port', type=int, default=65432, metavar='', help='port used for the connection')
    parser.add_argument('-c', '--cmd', default='', metavar='', help='command used for the connection')
    parser.add_argument('-t', '--timeout', type=int, default=0, metavar='', help='timespan before client automatically ends the connection (in sec)')
    
    return parser

def get_arguments(parser) -> Tuple[dict, dict]:
    args = parser.parse_args()
    dict = vars(args)
    public_dict = {k:dict[k] for k in dict.keys() if k not in private_info}
    private_dict = {k:dict[k] for k in dict.keys() if k in private_info}
    return (public_dict, private_dict)

def stop_client(*args):
    Log.log(Log.warn_level, "Timeout reached, stoping the client")
    raise KeyboardInterrupt

def launchClient(user: User) -> None:
    if user.get_user_info("timeout") != 0:
        Log.log(Log.info_level, "Timeout in {} seconds, setting an alarm".format(user.get_user_info("timeout")))
        signal.signal(signal.SIGALRM, stop_client)
        signal.alarm(user.get_user_info("timeout"))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((user.get_user_info("address"), user.get_user_info("port")))
    
    #dumping user's public info to send them to the server
    payload = user.json_dump()
    msg = ComProtocole.generate_msg(ComHeaders.INTRODUCE, payload)
    Log.log(Log.info_level, "Sending: {}".format(payload))
    s.sendall(msg.encode())

    while user.is_com_active():
        try:
            data = s.recv(1024)
        except KeyboardInterrupt:
            break
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

    # Handling socket closure                
    s.sendall(ComProtocole.generate_msg(ComHeaders.END_CONNECTION).encode())
    data = s.recv(1024)
    msg_header, payload = ComProtocole.decode_msg(data.decode())
    action_list[msg_header.value](user, payload)
    s.close()

def main(argv):
    parser = setup_argument_parser()
    public_dict, private_dict = get_arguments(parser)

    # Adding client parameters into user object 
    user = User(public_dict)

    user.add_private_info(private_dict)

    # Adding logger to user context
    user.register_logger(Log)

    init_action_list()

    Log.log(Log.info_level, "launching connection manager") 

    launchClient(user)
    Log.log(Log.info_level, "client exit")
    time.sleep(1)
    log_mgr.stop_logger_mgr()

if __name__ == "__main__":
    main(sys.argv[1:])