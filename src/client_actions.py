#!/usr/bin/env python3

import sys
from display import Logger
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders
import os
import subprocess

def pass_fct(*args):
    pass

def end_client_connection(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))
    user.desactivate_com()

def client_registration_ack(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))
    user.update_from_json(payload)

def wait_for_resource(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))

def access_resource(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))
    cmd:str = user.get_user_info("cmd")
    if cmd:
        Log.log(Log.info_level, "Launching cmd : {}".format(cmd))
        proc = subprocess.Popen(cmd.split())
        try:
            proc.wait(timeout=user.get_user_info("timeout"))
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        subprocess.Popen(['reset']).wait()

    user.desactivate_com()

def invalid_msg(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.err_level, "INVALID MESSAGE RECEIVED : {}".format(payload))

action_list = [pass_fct for _ in range(len(ComHeaders))]

def init_action_list() -> None:
    action_list[ComHeaders.END_CONNECTION.value] = end_client_connection
    action_list[ComHeaders.INTRODUCE.value] = client_registration_ack
    action_list[ComHeaders.WAIT.value] = wait_for_resource
    action_list[ComHeaders.FREE_RESOURCE.value] = access_resource
    action_list[ComHeaders.INVALID.value] = invalid_msg

if __name__ == "__main__":
    pass