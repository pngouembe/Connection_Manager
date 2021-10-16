#!/usr/bin/env python3

import sys
import time
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders, ComProtocole
import json
from socket import socket
import global_vars

def pass_fct(*args):
    pass

def send_resource_freed_msg(user: User) -> None:
    if len(User.get_user_list()) > 1 and user == User.get_first_user_in_line():
        next_user = User.get_next_user_in_line(user)
        new_client:socket = next_user.get_user_info("socket_obj")
        msg = ComProtocole.generate_msg(ComHeaders.FREE_RESOURCE, "Resource is free!")
        # TODO find a way to allow accidental deconnexion to come back
        #time.sleep(global_vars.resource_free_delay)
        new_client.sendall(msg.encode())


def client_connection_timeout(user: User) -> None:
    client:socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.TIMEOUT,
                                    "Timeout of {}s reached, connection ended".format(
                                        user.get_user_info("timeout")
                                    ))
    client.sendall(msg.encode())
    user.desactivate_com()

    send_resource_freed_msg(user)

def end_client_connection(user: User, payload: str) -> None:
    client:socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.END_CONNECTION,
                                    "Connection ended per client request")
    client.sendall(msg.encode())
    user.desactivate_com()

    send_resource_freed_msg(user)

def add_client_to_user_list(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()

    user.update(json.loads(payload))

    if user.get_user_info("timeout") != 0:
        timeout = min(global_vars.max_client_execution_time, user.get_user_info("timeout"))
    else:
        timeout = global_vars.max_client_execution_time

    user.update({"timeout": timeout})

    Log.log(Log.info_level, "Timeout set to {}s for {}".format(
            user.get_user_info("timeout"),
            user.get_user_name()
        ))

    client: socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.INTRODUCE, "Client registered in wait list")
    client.sendall(msg.encode())

    first_in_line: User = User.get_first_user_in_line()

    if user == first_in_line:
        msg = ComProtocole.generate_msg(ComHeaders.FREE_RESOURCE, "Resource is free!")
        client.sendall(msg.encode())
    else:
        msg_str = "Resource is taken by {}, comment: {}".format(first_in_line.get_user_name(),
                                                                first_in_line.get_user_info("comment"))
        msg = ComProtocole.generate_msg(ComHeaders.WAIT, msg_str)
        client.sendall(msg.encode())
        msg_str = "Currently waiting: {}".format(first_in_line.get_waiting_list())
        msg = ComProtocole.generate_msg(ComHeaders.WAIT, msg_str)
        client.sendall(msg.encode())

    Log.log(Log.dbg_level, "new client accepted : {}".format(user.get_user_name()))
    Log.log(Log.dbg_level, "client list : {}".format(user.get_user_names_list()))

action_list = [pass_fct for _ in range(len(ComHeaders))]

def init_action_list() -> None:
    action_list[ComHeaders.END_CONNECTION.value] = end_client_connection
    action_list[ComHeaders.INTRODUCE.value] = add_client_to_user_list

if __name__ == "__main__":
    pass