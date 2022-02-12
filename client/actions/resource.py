import re
from queue import Queue

from client.actions.utils import action, invalid_handling
from com import message
from com.header import Header
from com.message import Message
from users import User


@action(Header.FREE_RESOURCE)
def free_resource_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    read_queue.put(msg)
    return True


@action(Header.TIMEOUT)
def timeout_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    read_queue.put(msg)
    return True


@action(Header.STATUS)
def status_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    # Getting the ids of the resources from the message payload
    read_queue.put(msg)
    return True


@action(Header.WAIT)
def wait_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    read_queue.put(msg)
    return True


@action(Header.REQUEST_RESOURCE)
def request_resource_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    return invalid_handling("REQUEST_RESOURCE cannot be sent by server")


@action(Header.RELEASE_RESOURCE)
def release_resource_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    return invalid_handling("RELEASE_RESOURCE cannot be sent by server")