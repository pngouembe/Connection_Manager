import multiprocessing
from typing import List, Tuple
import unittest
from com import Header, message
from socket import socket, AF_INET, SOCK_STREAM, setdefaulttimeout
from sdataclasses.resources import Resource
from sdataclasses.servers import Server
from sdataclasses.uniquedataclass.users import User
from server import launch_server, socket_timeout
from signal import SIGINT
from os import kill
from dataclasses import dataclass
from rich import print

import time


@dataclass
class UserStruct:
    """Class used to group the user and it's socket"""
    user: User
    socket: socket

class TestServerMethods(unittest.TestCase):
    test_num = 1    # Counter used to give different name to users
    user_num = 1    # Number of user per instanciated per test
    user_list: List[UserStruct] = []
    resource_list = [Resource("R0", 0)]
    user_name = "Test client"
    server_name = "Server"
    addr = ("127.0.0.1", 65432)

    @classmethod
    def setUpClass(cls):
        server = Server(cls.addr[0], cls.addr[1], cls.resource_list)
        cls.p = multiprocessing.Process(target=launch_server,
                                        args=(server,),
                                        name="Server process",
                                        daemon=True)
        cls.p.start()
        cls.server_pid = cls.p.pid
        setdefaulttimeout(socket_timeout * 2)
        # waiting for server to bind
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        kill(cls.server_pid, SIGINT)
        cls.p.join()
        print("Server thread ended")
        print("=" * 80, end="\n\n")

    def user_setUp(self, user_struct: UserStruct = None):
        pass

    def setUp(self) -> None:
        for _ in range(self.user_num):
            name = self.user_name + " " + str(TestServerMethods.test_num)
            TestServerMethods.test_num += 1
            user = User(name=name, address=self.addr[0])
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect(self.addr)
            user_struct = UserStruct(user, sock)
            self.user_list.append(user_struct)

        print()
        print(self._testMethodName.center(80, "="))
        print(f"User list:")
        print(self.user_list)

        for user_struct in self.user_list:
            # calling user specific setUp
            self.user_setUp(user_struct)

    def user_tearDown(self, user_struct: UserStruct = None):
        pass

    def tearDown(self) -> None:
        for user_struct in self.user_list:
            self.user_tearDown(user_struct)
            rcv_msg = self.recv_msg(user_struct)
            self.assertEqual(rcv_msg.header, Header.END_CONNECTION)
            user_struct.socket.close()

        self.user_list.clear()

        print("=" * 80, end="\n\n")

    def send_msg(self, msg: message.Message, user_struct: UserStruct = None) -> None:
        if not user_struct:
            user_struct = self.user_list[0]
        print(f"{user_struct.user.name} sending : {msg}")
        user_struct.socket.send(msg.encode())

    def recv_msg(self, user_struct: UserStruct = None) -> message.Message:
        if not user_struct:
            user_struct = self.user_list[0]

        msg = message.decode(user_struct.socket.recv(1024))[0]
        l = len(user_struct.user.name)
        print(f"{user_struct.user.name} received: {msg}")
        return msg

    def send_intro(self, user_struct: UserStruct = None):
        if not user_struct:
            user_struct = self.user_list[0]
        msg = message.Message(Header.INTRODUCE, user_struct.user.serialize())
        self.send_msg(msg, user_struct)
        rcv_msg = self.recv_msg(user_struct)
        self.assertEqual(rcv_msg.header, Header.CONNECTION_READY)

    def send_end_connection(self, user_struct: UserStruct = None):
        if not user_struct:
            user_struct = self.user_list[0]
        msg = message.Message(Header.END_CONNECTION, "session terminated")
        self.send_msg(msg, user_struct)

        rcv_msg = self.recv_msg(user_struct)
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)
