from socket import socket

import re
from actions import action, invalid_handling
from queue import Queue
from com import Header, message
from com.message import Message
from sdataclasses.uniquedataclass.users import User
from server.handlers.resoures_handler import (ResourceHandlerThread,
                                              ResourceRequest, ResourceRelease)


@action(Header.FREE_RESOURCE)
def free_resource_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    return invalid_handling("WAIT messages cannot be sent by clients")


@action(Header.TIMEOUT)
def timeout_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    pass


@action(Header.STATUS)
def status_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    ids = set(map(int, re.sub("\D", " ", msg.payload).split()))
    resource_list = [ResourceHandlerThread.resource_list[i] for i in ids]
    msg_to_send = "{}".format(resource_list)
    resp = message.generate(Header.STATUS, msg_to_send)
    sock.send(resp.encode())
    return True


@action(Header.WAIT)
def wait_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    return invalid_handling("WAIT messages cannot be sent by clients")


@action(Header.REQUEST_RESOURCE)
def request_resource_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    ids = set(map(int, re.sub("\D", " ", msg.payload).split()))
    try:
        req = ResourceRequest(resource_ids=ids, user=user, user_sock=sock)
    except ValueError as e:
        print(e)
        msg = message.generate(Header.INVALID, e.__str__())
        return False

    # Request is transferred to the Resource handler.
    # The resource handler will respond to the requester
    ResourceHandlerThread.handle_request(req, request_queue)
    return True


@action(Header.RELEASE_RESOURCE)
def release_resource_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    req = ResourceRelease(user=user, user_sock=sock)
    ResourceHandlerThread.handle_request(req, request_queue)
    msg = Message(Header.RELEASE_RESOURCE, "User resource released")
    sock.send(msg.encode())
    return True
