from queue import Queue

from client.actions.utils import action, invalid_handling
from com import message
from com.header import Header
from com.message import Message
from users import User


@action(Header.END_CONNECTION)
def end_connection_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    return True


@action(Header.PING)
def ping_handling(user: User, msg: Message, read_queue: Queue) -> bool:
    user.socket.send(message.pong().encode())
    print(f"Sent: {message.pong()}")
    return True
