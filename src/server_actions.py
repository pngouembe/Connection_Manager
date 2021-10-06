#!/usr/bin/env python3

import sys
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders, ComProtocole
import json

def pass_fct(*args):
    pass

def end_client_connection(user:User, payload: str) -> None:
    client = user.user_info["client_obj"]
    msg = ComProtocole.generate_msg(ComHeaders.END_CONNECTION, 
                                    "Connection ended per client request")
    client.sendall(msg.encode())
    user.desactivate_com()


def add_client_to_user_list(user:User, payload: str) -> None:

    user.update(json.loads(payload))
    client = user.user_info["client_obj"]
    msg = ComProtocole.generate_msg(ComHeaders.INTRODUCE, "Client registered in wait list")
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