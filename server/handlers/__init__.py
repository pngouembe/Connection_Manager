import threading
from socket import socket, timeout

from com import header, message
from sdataclasses.uniquedataclass.users import User

import actions


class ClientHandlerThread(threading.Thread):
    def __init__(self, client_data: User, client_socket: socket, run_event) -> None:
        self.client_data = client_data
        self.client_socket = client_socket
        self.run_event = run_event
        super().__init__(name=client_data.name)

    def run(self):
        print("{} thread launched".format(self.name))
        while self.run_event:
            try:
                msg = self.client_socket.recv(1024)
            except timeout:
                self.client_socket.send(message.ping().encode())
                try:
                    msg = self.client_socket.recv(1024)
                    msg_list = message.decode(msg)
                    ping_handled = False
                    for m in msg_list:
                        if m.header == header.PING:
                            if actions.handle(self.client_data,
                                              m.header, m.payload):
                                ping_handled = True
                            else:
                                err_msg = message.generate(
                                    header.END_CONNECTION, "Invalid ping response, ending connection")
                                self.client_socket.send(err_msg.encode())
                    if not ping_handled:
                        break
                except timeout:
                    print("No response from client")
                    break

            if not msg:
                break
            else:
                msg_list = message.decode(msg)
                print(msg_list)
        self.client_socket.close()
        self.client_data.__del__()
        print("Ending {} thread".format(self.name))
