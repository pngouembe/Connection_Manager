from users import User
import threading
from socket import socket, timeout
from com import message


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
                    exp_msg = message.pong()
                    assert exp_msg in msg.decode()
                except timeout:
                    print("No response from client")
                    break
                except AssertionError:
                    print("Client response to ping is incorrect")
                    break

            if not msg:
                break
            else:
                msg_list = message.decode(msg.decode())
                print(msg_list)
        self.client_socket.close()
        print("Ending {} thread".format(self.name))
