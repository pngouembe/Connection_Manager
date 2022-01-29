from socket import socket
from queue import Queue
from actions import action, invalid_handling
from com import Header, message
from com.message import Message
from sdataclasses.uniquedataclass.users import User
from server.handlers.resoures_handler import ResourceHandlerThread, ResourceRelease
import re


@action(Header.END_CONNECTION)
def end_connection_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    # The closure of the socket is handled by the client handling thread
    msg_to_send = "Ending connection for {}: {}".format(user.name, msg.payload)
    resp = message.generate(Header.END_CONNECTION, msg_to_send)
    sock.send(resp.encode())

    return True


@action(Header.INTRODUCE)
def introduction_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    # User are introduce once and before launching the client handler thread
    return invalid_handling("Introduction already received")


@action(Header.PING)
def ping_handling(user: User, sock: socket, msg: Message, request_queue: Queue) -> bool:
    if 'pong' == msg.payload:
        return True
    else:
        print("Client response to ping is incorrect")
        return False
