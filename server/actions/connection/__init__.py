from queue import Queue

from actions import action
from com import Header, message
from com.message import Message
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
    # TODO: Investigate why invalid_handling resolve to NoneType
    # return invalid_handling("Introduction already received")
    print("Introduction already received")
    return False


@action(Header.PING)
def ping_handling(user: User, msg: Message, request_queue: Queue) -> bool:
    if 'pong' == msg.payload:
        return True
    else:
        print("Client response to ping is incorrect")
        return False