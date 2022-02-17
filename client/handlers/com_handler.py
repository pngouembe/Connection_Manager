import threading
from queue import Queue

import client.actions.handle as actions
from com import message
from com.header import Header
from mylogger import clog
from users import User


class ServerNotReadyError(Exception):
    def __init__(self, *args: object) -> None:
        clog.info("Server not ready, unable to communicate")
        super().__init__(*args)

# TODO: Make common handler thread class


class ComThread(threading.Thread):

    def __init__(self, user: User, run_event: threading.Event, read_queue: Queue) -> None:
        self.user = user
        self.run_event = run_event
        self.read_queue = read_queue
        super().__init__(name=user.info.name)

    def run(self) -> None:
        clog.info("{} thread launched".format(self.name))
        msg = message.Message(Header.INTRODUCE, self.user.info.serialize())
        message.send(self.user.socket, msg)
        msg_list = message.recv(self.user.socket)
        if msg_list[0].header != Header.CONNECTION_READY:
            raise ServerNotReadyError

        while self.run_event.is_set():
            msg = self.user.socket.recv(1024)
            msg_list = message.decode(msg)
            for m in msg_list:
                actions.handle(self.user, m, self.read_queue)

        msg = message.Message(Header.END_CONNECTION, "Session terminated")
        message.send(self.user.socket, msg)
        msg_list = message.recv(self.user.socket)
