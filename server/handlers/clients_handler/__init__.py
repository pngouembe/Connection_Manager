import threading
from queue import Queue
from socket import timeout
from time import sleep

import actions  # TODO: debug "from server import actions", it's not working
from com import Header, message
from handlers.resoures_handler import ResourceHandlerThread, ResourceRelease
from users import User


class ClientHandlerThread(threading.Thread):
    def __init__(self, user: User, run_event: threading.Event, request_queue: Queue) -> None:
        self.user = user
        self.run_event = run_event
        self.request_queue = request_queue
        self.wait_for_recovery = False
        super().__init__(name=user.info.name)

    def run(self):
        print("{} thread launched".format(self.name))
        ready_msg = message.generate(Header.CONNECTION_READY,
                                     "Server ready for communication")
        self.user.socket.send(ready_msg.encode())
        while self.run_event.is_set():
            if self.wait_for_recovery:
                if self.user.recovery_time == 0:
                    break
                else:
                    print("Waiting {}s for {} to reconnect".format(
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
                        self.wait_for_recovery = False

            try:
                msg = self.user.socket.recv(1024)
            except timeout:
                self.user.socket.send(message.ping().encode())
                try:
                    msg = self.user.socket.recv(1024)
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
                        self.wait_for_recovery = True
                        continue

                except timeout:
                    print("No response from client")
                    err_msg = message.generate(
                        Header.END_CONNECTION, "No response from client")
                    self.user.socket.send(err_msg.encode())
                    self.wait_for_recovery = True
                    continue

            if not msg:
                continue
            else:
                msg_list = message.decode(msg)
                for m in msg_list:
                    actions.handle(self.user, m, self.request_queue)
                    if m.header == Header.END_CONNECTION:
                        self.wait_for_recovery = True
                        break

        # Freeing the resources used
        req = ResourceRelease(user=self.user)

        if ResourceHandlerThread.handle_request(req, self.request_queue):
            msg_str = "User successfully removed from resource list"
        else:
            msg_str = "Error while removing user from resource list"

        msg = message.generate(Header.END_CONNECTION, msg_str)
        self.user.socket.send(msg.encode())

        # TODO: Find a better way to handle last message sending
        sleep(.1)

        self.user.socket.close()
        self.user.info.__del__()
        del self.user
        print("Ending {} thread".format(self.name))
