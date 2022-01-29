import multiprocessing
import unittest
from com import Header, message
from socket import socket, AF_INET, SOCK_STREAM, setdefaulttimeout
from sdataclasses.resources import Resource
from sdataclasses.servers import Server
from sdataclasses.uniquedataclass.users import User
from server import launch_server, socket_timeout
from signal import SIGINT
from os import kill

import time


class TestServerMethods(unittest.TestCase):
    test_num = 1

    @classmethod
    def setUpClass(cls):
        cls.addr = ("127.0.0.1", 65432)
        server = Server(cls.addr[0], cls.addr[1], [Resource("R0", 0)])
        cls.p = multiprocessing.Process(target=launch_server, args=(
            server,), name="Server process", daemon=True)
        cls.p.start()
        cls.server_pid = cls.p.pid
        setdefaulttimeout(socket_timeout * 2)
        cls.user_name = "Test client"
        # waiting for server to bind
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        kill(cls.server_pid, SIGINT)
        cls.p.join()
        print("Server thread ended")

    def setUp(self) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(self.addr)
        name = self.user_name + " " + str(TestServerMethods.test_num)
        self.user = User(name=name, address=self.addr[0])
        print()
        print(self._testMethodName.center(80, "="))
        print(self.user)
        TestServerMethods.test_num += 1

    def tearDown(self) -> None:
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)
        self.sock.close()
        print("=" * 80, end="\n\n")

    def send_msg(self, msg: message.Message) -> None:
        self.sock.send(msg.encode())
        print(f"Sent : {msg}")

    def recv_msg(self) -> message.Message:
        msg = message.decode(self.sock.recv(1024))[0]
        print(f"Rcvd : {msg}")
        return msg

    def send_intro(self):
        self.send_msg(message.Message(Header.INTRODUCE, self.user.serialize()))
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.CONNECTION_READY)

    def send_pong(self):
        self.sock.send(message.pong().encode())

    def send_end_connection(self):
        msg = message.Message(Header.END_CONNECTION, "session terminated")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)


class TestServerConnectionMethods(TestServerMethods):
    def test_no_introduction(self):
        time.sleep(socket_timeout + .1)

    def test_send_intro(self):
        self.send_intro()
        data = self.sock.recv(1024)
        self.assertEqual(data.decode(), message.ping())

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)

    def test_send_pong(self):
        self.send_intro()
        data = self.sock.recv(1024)
        self.assertEqual(data.decode(), message.ping())
        self.send_pong()

        # Sending a incorrect pong to see server reaction
        data = self.sock.recv(1024)
        self.assertEqual(data.decode(), message.ping())
        self.sock.send(message.ping().encode())

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)

    def test_send_end_connection(self):
        self.send_intro()

        self.send_end_connection()


class TestServerResourceMethods(TestServerMethods):
    def setUp(self) -> None:
        super().setUp()
        self.send_intro()

    def tearDown(self) -> None:
        self.send_end_connection()
        super().tearDown()

    def test_send_request_resource(self):
        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.WAIT)

    def test_send_status(self):        # Getting current status
        msg = message.Message(Header.STATUS, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        print(rcv_msg)
        self.assertEqual(rcv_msg.header, Header.STATUS)

        # Requesting resource
        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

        # Getting current status
        msg = message.Message(Header.STATUS, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.STATUS)

    def test_send_release_resource(self):
        # Requesting resource
        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

        # Getting current status
        msg = message.Message(Header.STATUS, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.STATUS)

        msg = message.Message(Header.RELEASE_RESOURCE, "")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.RELEASE_RESOURCE)

        # Getting current status
        msg = message.Message(Header.STATUS, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.STATUS)


if __name__ == '__main__':
    unittest.main()
