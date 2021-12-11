#!/usr/bin/env python3

import sys
from display import Logger
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders
import os
import global_vars
import subprocess

def pass_fct(*args):
    pass

def end_client_connection(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.info_level, "Received : {}".format(payload))
    user.desactivate_com()


def client_connection_timeout(user: User, payload: str) -> None:
    Log: Logger = user.get_logger()
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
        if user.get_user_info("timeout") != 0:
            timeout = user.get_user_info("timeout")
        else:
            timeout = None
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            Log.log(Log.warn_level, "Timout expired for cmd : {}".format(cmd))
            proc.kill()
            proc.wait()
            user.timed_out()
        subprocess.Popen(['reset']).wait()
    else:
        Log.log(Log.warn_level, "No command passed, relaunch client with a command")
        Log.log(Log.warn_level, "Resource will be released in {}s".format(global_vars.resource_free_delay))
    user.desactivate_com()

def invalid_msg(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.err_level, "INVALID MESSAGE RECEIVED : {}".format(payload))

def user_update(user: User, payload: str) -> None:
    Log:Logger = user.get_logger()
    Log.log(Log.info_level, "Update received : {}".format(payload))
    user.update_from_json(payload)


action_list = [pass_fct for _ in range(len(ComHeaders))]

def init_action_list() -> None:
    action_list[ComHeaders.END_CONNECTION.value] = end_client_connection
    action_list[ComHeaders.INTRODUCE.value] = client_registration_ack
    action_list[ComHeaders.WAIT.value] = wait_for_resource
    action_list[ComHeaders.FREE_RESOURCE.value] = access_resource
    action_list[ComHeaders.INVALID.value] = invalid_msg
    action_list[ComHeaders.UPDATE.value] = user_update
    action_list[ComHeaders.TIMEOUT.value] = client_connection_timeout

if __name__ == "__main__":
    pass
