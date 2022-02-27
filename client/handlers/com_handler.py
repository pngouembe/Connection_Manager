import threading
import time
from queue import Empty, Queue
from socket import timeout

import client.actions.handle as actions
from com import message
from com.header import Header
from mydataclasses.uniquedataclass import DuplicateError
from mylogger import clog
from users import User

# TODO: Make common handler thread class


class ComThread(threading.Thread):

    def __init__(self, user: User, run_event: threading.Event, queue: Queue) -> None:
        self.user = user
        self.run_event = run_event
        self.queue = queue
        super().__init__(name=user.info.name)

# TODO: Investigate need for in and out queues
class ClientComThread(ComThread):
    def __init__(self, user: User, run_event: threading.Event, queue: Queue) -> None:
        # TODO: make refresh interval configurable
        # Time in sec between two automatic status request
        self.refresh_interval = 3
        super().__init__(user, run_event, queue)

    def run(self) -> None:
        clog.info("{} thread launched".format(self.name))

        start_time = cur_time = time.time()
        while self.run_event.is_set():

            try:
                msg_list = message.recv(self.user.socket)
            except timeout:
                continue

            for m in msg_list:
                actions.handle(self.user, m, self.queue)
            if cur_time - start_time > self.refresh_interval:
                msg = message.Message(
                    Header.STATUS,
                    ",".join(self.user.requested_resources)
                )
                message.send(self.user.socket, msg)
                start_time = time.time()
            cur_time = time.time()

        msg = message.Message(Header.END_CONNECTION, "Session terminated")
        message.send(self.user.socket, msg)
        msg_list = message.recv(self.user.socket)
