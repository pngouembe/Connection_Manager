from queue import Queue
import threading
from socket import socket, timeout
from time import sleep

import actions  # TODO: debug "from server import actions", it's not working
from com import Header, message
from handlers.resoures_handler import ResourceHandlerThread, ResourceRelease
from sdataclasses.uniquedataclass.users import User


class ClientHandlerThread(threading.Thread):
    wait_for_recovery = False

    def __init__(self, client_data: User, client_socket: socket, run_event: threading.Event, request_queue: Queue) -> None:
        self.client_data = client_data
        self.client_socket = client_socket
        self.run_event = run_event
        self.request_queue = request_queue
        self.resource_request_handled = False
        super().__init__(name=client_data.name)

    def run(self):
        print("{} thread launched".format(self.name))
        connection_ended = False
        ready_msg = message.generate(Header.CONNECTION_READY,
                                     "Server ready for communication")
        self.client_socket.send(ready_msg.encode())
        while self.run_event.is_set():
            if self.wait_for_recovery:
                # TODO: handle client reconnection
                break
            try:
                msg = self.client_socket.recv(1024)
            except timeout:
                self.client_socket.send(message.ping().encode())
                try:
                    msg = self.client_socket.recv(1024)
                    msg_list = message.decode(msg)
                    ping_handled = False
                    for m in msg_list:
                        if m.header == Header.PING:
                            if actions.handle(self.client_data, self.client_socket, m, self.request_queue):
                                ping_handled = True
                            else:
                                err_msg = message.generate(
                                    Header.END_CONNECTION, "Invalid ping response, ending connection")
                                self.client_socket.send(err_msg.encode())
                    if not ping_handled:
                        break
                except timeout:
                    print("No response from client")
                    err_msg = message.generate(
                        Header.END_CONNECTION, "No response from client")
                    self.client_socket.send(err_msg.encode())
                    break

            if not msg:
                break
            else:
                msg_list = message.decode(msg)
                for m in msg_list:
                    actions.handle(self.client_data,
                                   self.client_socket, m, self.request_queue)
                    if m.header == Header.END_CONNECTION:
                        connection_ended = True
                        break
            if connection_ended:
                break

        # Freeing the resources used
        req = ResourceRelease(user=self.client_data,
                              user_sock=self.client_socket)

        self.resource_request_handled = False
        if ResourceHandlerThread.handle_request(req, self.request_queue):
            msg_str = "User successfully removed from resource list"
        else:
            msg_str = "Error while removing user from resource list"

        msg = message.generate(Header.END_CONNECTION, msg_str)
        self.client_socket.send(msg.encode())

        # TODO: Find a better way to handle last message sending
        sleep(.1)

        self.client_socket.close()
        self.client_data.__del__()
        print("Ending {} thread".format(self.name))
