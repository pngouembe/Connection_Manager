from queue import Queue

from com import message
from com.header import Header
from com.message import Message
from mylogger import log
from server.actions.utils import action, invalid_handling
from users import User


@action(Header.END_CONNECTION)
def end_connection_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    # The closure of the socket is handled by the client handling thread
    msg_to_send = "Ending connection for {}: {}".format(
        user.info.name, msg.payload)
    resp = message.generate(Header.END_CONNECTION, msg_to_send)
    user.socket.send(resp.encode())

    return True


@action(Header.INTRODUCE)
def introduction_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    # User are introduce once and before launching the client handler thread
    return invalid_handling("Introduction already received")


@action(Header.PING)
def ping_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    if 'pong' == msg.payload:
        return True
    else:
        log.info("Client response to ping is incorrect")
        return False
