from socket import socket, AF_INET, SOCK_STREAM
import unittest

from com import Header, message
from users import User

from . import TestServerMethods, server_socket_timeout


class TestServerMultipleUser(TestServerMethods):
    user_num = 2

    def user_setUp(self, user: User = None) -> None:
        self.send_intro(user)

    def user_tearDown(self, user: User = None) -> None:
        self.send_end_connection(user)

    def test_free_resource_notification(self):
        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg, self.user_list[0])

        rcv_msg = self.recv_msg(self.user_list[0])
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg, self.user_list[1])

        rcv_msg = self.recv_msg(self.user_list[1])
        self.assertEqual(rcv_msg.header, Header.WAIT)

        msg = message.Message(Header.RELEASE_RESOURCE, "")
        self.send_msg(msg, self.user_list[0])

        rcv_msg = self.recv_msg(self.user_list[0])
        self.assertEqual(rcv_msg.header, Header.RELEASE_RESOURCE)

        rcv_msg = self.recv_msg(self.user_list[1])
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)


if __name__ == '__main__':
    unittest.main()
