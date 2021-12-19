#!/usr/bin/env python3

import sys
import time
from datetime import datetime
sys.path.append('../modules')
from user import User
from com_protocole import ComHeaders, ComProtocole
import json
from socket import socket
import global_vars
from display import Logger


def pass_fct(*args):
    pass


def send_resource_freed_msg(user: User, msg: str = "Resource is free!") -> None:
    client: socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.FREE_RESOURCE, msg)
    client.sendall(msg.encode())


def send_resource_freed_msg_to_next_in_line(user: User, skip_rety: bool = False) -> None:
    Log: Logger = user.get_logger()
    retry_cnt = 0
    if not skip_rety:
        log_str = "Waiting {}s in case {} reconnects".format(
            global_vars.resource_free_delay, user.get_user_name())
        Log.log(Log.dbg_level, log_str)

    while retry_cnt < global_vars.reconnexion_retries and not skip_rety:
        try:
            time.sleep(global_vars.resource_free_delay /
                       global_vars.reconnexion_retries)
            if user.is_trying_to_reconnect():
                user_retry: User = User.get_user_reconnexion_attempt(user)
                elapsed_time = int(datetime.utcnow().timestamp()) - \
                    int(user.get_user_info("start_time"))
                timeout = max(
                    int(user.get_user_info("timeout")) - elapsed_time, 0)
                print(user_retry)
                user_retry.update(
                    {"timeout": timeout, "start_time": user.get_user_info("start_time")})
                user.set_as_duplicate()
                user.desactivate_com()
                User.set_next_user_in_line(user_retry)
                client: socket = user_retry.get_user_info("socket_obj")
                msg = ComProtocole.generate_msg(
                    ComHeaders.UPDATE, user_retry.json_dump())
                client.sendall(msg.encode())
                send_resource_freed_msg(
                    user_retry,
                    msg="Resource re attributed to you, remaining time: {}s".format(
                        timeout)
                )
                log_str = "{} trying to reconnect, granting resource".format(
                    user_retry.get_user_name())
                Log.log(Log.dbg_level, log_str)
                break
            retry_cnt += 1
        except KeyboardInterrupt:
            break

    # if user is not reconnecting
    if retry_cnt >= global_vars.reconnexion_retries or skip_rety:
        if len(User.get_user_list()) > 1 and user == User.get_first_user_in_line():
            next_user: User = User.get_next_user_in_line(user)
            Log.log(Log.dbg_level, "giving resource to {}".format(
                next_user.get_user_name()))
            send_resource_freed_msg(next_user)
            user.desactivate_com()
        user.remove_from_resource_waiting_list()


def client_connection_timeout(user: User, payload: str) -> None:
    client: socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.TIMEOUT,
                                    "Timeout of {}s reached, connection ended".format(
                                        user.get_user_info("timeout")
                                    ))
    client.sendall(msg.encode())

    send_resource_freed_msg_to_next_in_line(user, skip_rety=True)


def end_client_connection(user: User, payload: str) -> None:
    client: socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.END_CONNECTION,
                                    "Connection ended per client request")
    client.sendall(msg.encode())

    send_resource_freed_msg_to_next_in_line(user)


def add_client_to_user_list(user: User, payload: str) -> None:
    Log: Logger = user.get_logger()

    user.update_from_json(payload)
    user.update(
        {"start_time": datetime.utcnow().replace(microsecond=0).timestamp()})
    log_str = "new client accepted : {} at {} UTC".format(
        user.get_user_name(),
        datetime.fromtimestamp(user.get_user_info("start_time")))
    Log.log(Log.dbg_level, log_str)
    Log.log(Log.dbg_level, "client list : {}".format(
        user.get_user_names_list()))
    if user.get_user_info("timeout") != 0 and global_vars.max_client_execution_time != 0:
        timeout = min(global_vars.max_client_execution_time,
                      user.get_user_info("timeout"))
    elif user.get_user_info("timeout") == 0 and global_vars.max_client_execution_time != 0:
        timeout = global_vars.max_client_execution_time
    else:
        timeout = user.get_user_info("timeout")
    user.update({"timeout": timeout})

    Log.log(Log.info_level, "Timeout set to {}s for {}".format(
            user.get_user_info("timeout"),
            user.get_user_name()
            ))

    client: socket = user.get_user_info("socket_obj")
    msg = ComProtocole.generate_msg(ComHeaders.INTRODUCE, user.json_dump())
    client.sendall(msg.encode())

    if user.is_next_in_line():
        msg = ComProtocole.generate_msg(
            ComHeaders.FREE_RESOURCE, "Resource is free!")
        client.sendall(msg.encode())
    else:
        first_in_line: User = User.get_first_user_in_line()
        user.add_to_resource_waiting_list()
        msg_str = "Resource is taken by {}, comment: {}".format(first_in_line.get_user_name(),
                                                                first_in_line.get_user_info("comment"))
        msg = ComProtocole.generate_msg(ComHeaders.WAIT, msg_str)
        client.sendall(msg.encode())
        msg_str = "Currently waiting: {}".format(
            first_in_line.get_waiting_list())
        msg = ComProtocole.generate_msg(ComHeaders.WAIT, msg_str)
        client.sendall(msg.encode())


action_list = [pass_fct for _ in range(len(ComHeaders))]


def init_action_list() -> None:
    action_list[ComHeaders.END_CONNECTION.value] = end_client_connection
    action_list[ComHeaders.INTRODUCE.value] = add_client_to_user_list
    action_list[ComHeaders.TIMEOUT.value] = client_connection_timeout


if __name__ == "__main__":
    pass
