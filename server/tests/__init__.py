import multiprocessing
import time
import unittest
from os import kill
from signal import SIGINT
from socket import AF_INET, SOCK_STREAM, setdefaulttimeout, socket
from typing import List, Tuple

from com import Header, message
from rich import print
from sdataclasses.resources import Resource
from sdataclasses.servers import Server
from server import launch_server, socket_timeout
from users import User, UserInfo


class TestServerMethods(unittest.TestCase):
    test_num = 1    # Counter used to give different name to users
    user_num = 1    # Number of user per instanciated per test
    user_list: List[User] = []
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

    def user_setUp(self, user: User = None):
        pass

    def setUp(self) -> None:
        for _ in range(self.user_num):
            name = self.user_name + " " + str(TestServerMethods.test_num)
            TestServerMethods.test_num += 1
            user_info = UserInfo(name=name, address=self.addr[0])
            sock = socket(AF_INET, SOCK_STREAM)
            user = User(info=user_info, socket=sock)
            user.socket.connect(self.addr)
            self.user_list.append(user)

        print()
        print(self._testMethodName.center(80, "="))
        print(f"User list:")
        print(self.user_list)

        for user in self.user_list:
            # calling user specific setUp
            self.user_setUp(user)

    def user_tearDown(self, user: User = None):
        pass

    def tearDown(self) -> None:
        for user in self.user_list:
            self.user_tearDown(user)
            rcv_msg = self.recv_msg(user)
            self.assertEqual(rcv_msg.header, Header.END_CONNECTION)
            user.socket.close()

        self.user_list.clear()

        print("=" * 80, end="\n\n")

    def send_msg(self, msg: message.Message, user: User = None) -> None:
        if not user:
            user = self.user_list[0]
        print(f"{user.info.name} sending : {msg}")
        user.socket.send(msg.encode())

    def recv_msg(self, user: User = None) -> message.Message:
        if not user:
            user = self.user_list[0]

        msg = message.decode(user.socket.recv(1024))[0]
        l = len(user.info.name)
        print(f"{user.info.name} received: {msg}")
        return msg

    def send_intro(self, user: User = None):
        if not user:
            user = self.user_list[0]
        msg = message.Message(Header.INTRODUCE, user.info.serialize())
        self.send_msg(msg, user)
        rcv_msg = self.recv_msg(user)
        self.assertEqual(rcv_msg.header, Header.CONNECTION_READY)

    def send_end_connection(self, user: User = None):
        if not user:
            user = self.user_list[0]
        msg = message.Message(Header.END_CONNECTION, "session terminated")
        self.send_msg(msg, user)

        rcv_msg = self.recv_msg(user)
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)