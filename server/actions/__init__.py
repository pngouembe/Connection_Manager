
from queue import Queue

from com import Header, header_list
from com.message import Message
from users import User

action_list = []


def pass_fct(*args, **kwargs):
    pass


for i in header_list:
    action_list.append(pass_fct)


def action(com_header: Header):
    global action_list

    def wrap(func):
        action_list[com_header.value] = func
    return wrap


@action(Header.INVALID)
def invalid_handling(msg):
    print(msg)
    return False


def handle(user: User, msg: Message, request_queue: Queue) -> bool:
    """
    Execute the registered action for the message type received.
    Return True if the handling was successful otherwise return False
    """
    return action_list[msg.header.value](user, msg, request_queue)
