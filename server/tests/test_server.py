from contextlib import closing
import multiprocessing
import unittest
from com import header, message
from dataclass import MissingRequiredFields, Server, server_from_dict
from dataclasses import asdict, FrozenInstanceError
from socket import socket, AF_INET, SOCK_STREAM, timeout, setdefaulttimeout
from users import User
from server import launch_server, socket_timeout
from signal import SIGINT
from os import kill, name

from server.handlers import ClientHandlerThread
import time


class TestServerDataclassMethods(unittest.TestCase):
    def test_server_from_dict(self):
        self.server_dict = {
            "address": "127.0.0.1",
            "port": 0,
            "foo": "bar",
            "id": 0,
            "a": 10}
        self.server = server_from_dict(self.server_dict)
        self.assertEqual(asdict(self.server), self.server_dict)

        # checking that the class is read-only
        with self.assertRaises(FrozenInstanceError):
            self.server.port = 1

        # testing required fields
        self.server_dict = {
            "address": "127.0.0.1",
            "foo": "bar",
            "id": 0,
            "a": 10}
        with self.assertRaises(MissingRequiredFields):
            self.server = server_from_dict(self.server_dict)

        with self.assertRaises(MissingRequiredFields):
            self.server = server_from_dict({})


class TestServerMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.addr = ("127.0.0.1", 65432)
        server = Server(cls.addr[0], cls.addr[1])
        cls.user = User(name="Test client", address=cls.addr[0])
        cls.p = multiprocessing.Process(target=launch_server, args=(server,), name="Server process", daemon=True)
        cls.p.start()
        cls.server_pid = cls.p.pid
        setdefaulttimeout(socket_timeout*2)

    @classmethod
    def tearDownClass(cls):
        kill(cls.server_pid, SIGINT)
        cls.p.join()
        print("Server thread ended")

    def setUp(self) -> None:
        self.sock = socket(AF_INET, SOCK_STREAM)
        print("creating socked {}".format(self.sock.fileno()))
        self.sock.connect(self.addr)

    def tearDown(self) -> None:
        self.sock.close()

    def test_no_introduction(self):
        time.sleep(socket_timeout + .1)

    def test_send_intro(self):
        msg = message.generate(header.INTRODUCE, self.user.serialize())
        self.sock.send(msg.encode())
        data = self.sock.recv(1024)
        self.assertEqual(data.decode(), message.ping())


# class TestServerHandlersMethods(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.s = socket(AF_INET, SOCK_STREAM)
#         cls.client_s = socket(AF_INET, SOCK_STREAM)
#         cls.s.settimeout(1)
#         cls.run_event = threading.Event()
#         cls.run_event.set()
#         user = User(name="Test client", address="127.0.0.1", resource=0)
#         cls.client_handler = ClientHandlerThread(client_data=user,client_socket=cls.s, run_event=cls.run_event)
#         cls.client_handler.start()

#     @classmethod
#     def tearDownClass(cls):
#         cls.run_event.clear()
#         cls.client_handler.join()

#     def test_dummy(self):
#         print("dummy test")
