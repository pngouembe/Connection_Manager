from queue import Queue

from client.actions.utils import action, invalid_handling
from com import message
from com.header import Header
from com.message import Message
from mylogger import log
from users import User


@action(Header.END_CONNECTION)
def end_connection_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    return True


@action(Header.INTRODUCE)
def introduction_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    pass

@action(Header.PING)
def ping_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    user.socket.send(message.pong().encode())
    log.debug(f"Sent: {message.decode(message.pong())[0]}")
    return True
