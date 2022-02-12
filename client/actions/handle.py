from queue import Queue

from com.message import Message
from client.actions.utils import action_list
from users import User


def handle(user: User, msg: Message, read_queue: Queue) -> bool:
    """
    Execute the registered action for the message type received.
    Return True if the handling was successful otherwise return False
    """
    return action_list[msg.header.value](user, msg, read_queue)
