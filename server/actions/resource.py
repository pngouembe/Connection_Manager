import re
from queue import Queue

from com import message
from com.header import Header
from com.message import Message
from mylogger import clog
from server.actions.utils import action, invalid_handling
from server.handlers.resources_handler import (ResourceHandlerThread,
                                               ResourceRelease,
                                               ResourceRequest)
from users import User


@action(Header.FREE_RESOURCE)
def free_resource_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    return invalid_handling("FREE_RESOURCE messages cannot be sent by clients")


@action(Header.TIMEOUT)
def timeout_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    pass


# TODO: Add support for querying status of all the resources
@action(Header.STATUS)
def status_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    # Getting the ids of the resources from the message payload
    if msg.payload:
        ids = set(map(int, re.sub("\D", " ", msg.payload).split()))
        resource_list = [ResourceHandlerThread.resource_list[i] for i in ids]
    else:
        resource_list = ResourceHandlerThread.resource_list
    for r in resource_list:
        resp = message.generate(Header.STATUS, r.serialize())
        user.socket.send(resp.encode())
    return True


@action(Header.WAIT)
def wait_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    return invalid_handling("WAIT messages cannot be sent by clients")


@action(Header.REQUEST_RESOURCE)
def request_resource_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    ids = set(map(int, re.sub("\D", " ", msg.payload).split()))
    try:
        req = ResourceRequest(resource_ids=ids, user=user)
    except ValueError as e:
        clog.error(e)
        msg = message.generate(Header.INVALID, e.__str__())
        return False

    # Request is transferred to the Resource handler.
    # The resource handler will respond to the requester
    ResourceHandlerThread.handle_request(req, request_queue)
    return True


@action(Header.RELEASE_RESOURCE)
def release_resource_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    req = ResourceRelease(user=user)
    ResourceHandlerThread.handle_request(req, request_queue)
    msg = Message(Header.RELEASE_RESOURCE, "User resource released")
    user.socket.send(msg.encode())
    return True
