#!/usr/bin/env python3

import sys
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders

def pass_fct(*args):
    pass

def end_client_connection(user:User, payload: str) -> None:
    Log = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))
    user.desactivate_com()

def client_registration_ack(user:User, payload: str) -> None:
    Log = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))

action_list = [pass_fct for _ in range(len(ComHeaders))]

def init_action_list() -> None:
    action_list[ComHeaders.END_CONNECTION.value] = end_client_connection
    action_list[ComHeaders.INTRODUCE.value] = client_registration_ack

if __name__ == "__main__":
    pass