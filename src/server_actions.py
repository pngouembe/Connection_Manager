#!/usr/bin/env python3

import sys
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders, ComProtocole
import json

def pass_fct(*args):
    pass

def end_client_connection(user: User, payload: str) -> None:
    client = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.END_CONNECTION, 
                                    "Connection ended per client request")
    client.sendall(msg.encode())
    user.desactivate_com()

    if len(User.get_user_list()) > 1 and user == User.get_first_user_in_line():
        next_user = User.get_next_user_in_line(user)
        new_client = next_user.get_user_info("socket_obj")
        msg = ComProtocole.generate_msg(ComHeaders.FREE_RESOURCE, "Resource is free!")
        new_client.sendall(msg.encode())

def add_client_to_user_list(user: User, payload: str) -> None:

    user.update(json.loads(payload))
    client = user.get_user_info("socket_obj")
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

    Log = user.get_logger()
    Log.log(Log.dbg_level, "new client accepted : {}".format(user.get_user_name()))
    Log.log(Log.dbg_level, "client list : {}".format(user.get_user_names_list()))

action_list = [pass_fct for _ in range(len(ComHeaders))]

def init_action_list() -> None:
    action_list[ComHeaders.END_CONNECTION.value] = end_client_connection
    action_list[ComHeaders.INTRODUCE.value] = add_client_to_user_list

if __name__ == "__main__":
    pass