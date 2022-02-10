from socket import socket, AF_INET, SOCK_STREAM
from time import sleep, time
import unittest

from com import message
from com.header import Header
from users import User

from . import TestServerMethods, server_socket_timeout


class TestServerUserReconnection(TestServerMethods):
    user_num = 1
    resource_free_delay = server_socket_timeout + .1

    def user_setUp(self, user: User = None) -> None:
        self.send_intro(user)

    def user_tearDown(self, user: User = None) -> None:
        self.send_end_connection(user)

    def test_reconnection(self):
        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

        msg = message.Message(Header.END_CONNECTION, "session terminated")
        self.send_msg(msg, self.user_list[0])

        sock = socket(AF_INET, SOCK_STREAM)
        self.user_list[0] = User(info=self.user_list[0].info, socket=sock)
        self.user_list[0].socket.connect(self.addr)
        self.send_intro()

        msg = message.Message(Header.RELEASE_RESOURCE, "")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.RELEASE_RESOURCE)

    def test_reconnection_delay_expired(self):
        self.send_end_connection()

        sleep(self.resource_free_delay + .1)

        sock = socket(AF_INET, SOCK_STREAM)
        self.user_list[0] = User(info=self.user_list[0].info, socket=sock)
        self.user_list[0].socket.connect(self.addr)

        msg = message.Message(
            Header.INTRODUCE, self.user_list[0].info.serialize())
        self.send_msg(msg)
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.CONNECTION_READY)
        self.assertNotIn("reconnection", rcv_msg.payload)


if __name__ == '__main__':
    unittest.main()
