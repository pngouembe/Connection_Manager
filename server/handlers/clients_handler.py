import threading
from queue import Queue
from socket import timeout
from time import sleep

import server.actions.handle as actions
from com import message
from com.header import Header
from mylogger import clog
from server.handlers.resources_handler import (ResourceHandlerThread,
                                               ResourceRelease)
from users import User


class ClientHandlerThread(threading.Thread):
    def __init__(self, user: User, run_event: threading.Event, request_queue: Queue) -> None:
        self.user = user
        self.run_event = run_event
        self.request_queue = request_queue
        super().__init__(name=user.info.name)

    def run(self):
        clog.info("{} thread launched".format(self.name))
        ready_msg = message.generate(Header.CONNECTION_READY,
                                     "Server ready for communication")
        self.user.socket.send(ready_msg.encode())
        while self.run_event.is_set():
            if self.user.waiting_for_reconnection:
                if self.user.recovery_time == 0:
                    break
                else:
                    clog.info("Waiting {}s for {} to reconnect".format(
                        self.user.recovery_time, self.user.info.name))
                    r = self.user.reconnection_event.wait(
                        self.user.recovery_time)
                    if r == False:
                        break
                    else:
                        ready_msg = message.generate(Header.CONNECTION_READY,
                                                     "Successfull reconnection, server ready for communication")
                        self.user.socket.send(ready_msg.encode())
                        self.user.reconnection_event.clear()
                        self.user.waiting_for_reconnection = False

            try:
                msg = self.user.socket.recv(1024)
            except timeout:
                self.user.socket.send(message.ping().encode())
                try:
                    msg = self.user.socket.recv(1024)
                except timeout:
                    clog.info("No response from client")
                    err_msg = message.generate(
                        Header.END_CONNECTION, "No response from client")
                    self.user.socket.send(err_msg.encode())
                    self.user.waiting_for_reconnection = True
                    continue
                else:
                    msg_list = message.decode(msg)
                    ping_handled = False
                    for m in msg_list:
                        if m.header == Header.PING:
                            r = actions.handle(
                                self.user, m, self.request_queue)
                            if r:
                                ping_handled = True
                            else:
                                err_msg = message.generate(
                                    Header.END_CONNECTION, "Invalid ping response, ending connection")
                                self.user.socket.send(err_msg.encode())
                    if not ping_handled:
                        self.user.waiting_for_reconnection = True
                        continue

            if not msg:
                clog.info("No response from client")
                self.user.waiting_for_reconnection = True
            else:
                msg_list = message.decode(msg)
                for m in msg_list:
                    clog.info(m)
                    actions.handle(self.user, m, self.request_queue)
                    if m.header == Header.END_CONNECTION:
                        self.user.waiting_for_reconnection = True
                        break

        self.user.waiting_for_reconnection = False
        # Freeing the resources used
        req = ResourceRelease(user=self.user)

        if ResourceHandlerThread.handle_request(req, self.request_queue):
            msg_str = "User successfully removed from resource list"
        else:
            msg_str = "Error while removing user from resource list"

        msg = message.generate(Header.END_CONNECTION, msg_str)
        try:
            self.user.socket.send(msg.encode())
        except BrokenPipeError:
            # client already gone, socket closed
            pass

        # TODO: Find a better way to handle last message sending
        sleep(.1)

        self.user.socket.close()
        self.user.info.__del__()
        del self.user
        clog.info("Ending {} thread".format(self.name))
