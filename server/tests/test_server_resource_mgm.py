import unittest

from com import message
from com.header import Header
from mylogger import clog
from server.tests import TestServerMethods
from users import User


class TestServerResourceMethods(TestServerMethods):
    def user_setUp(self, user: User = None) -> None:
        self.send_intro()

    def user_tearDown(self, user: User = None) -> None:
        self.send_end_connection()

    def test_send_request_resource(self):
        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

        msg = message.Message(Header.REQUEST_RESOURCE, "0")
        self.send_msg(msg)

        # When you already posses the resource, you also receive FREE_RESOURCE
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.FREE_RESOURCE)

    def test_send_status(self):        # Getting current status
        msg = message.Message(Header.STATUS, "0")
        self.send_msg(msg)

        rcv_msg = self.recv_msg()
        clog.info(rcv_msg)
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
