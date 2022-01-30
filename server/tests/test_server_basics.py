import unittest
from com import Header, message

import time

from . import TestServerMethods, socket_timeout


class TestServerConnectionMethods(TestServerMethods):
    def test_no_introduction(self):
        time.sleep(socket_timeout + .1)

    def test_send_intro(self):
        self.send_intro()
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.PING)
        self.assertEqual(rcv_msg.payload, 'ping')

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)

    def test_send_pong(self):
        self.send_intro()
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.PING)
        self.assertEqual(rcv_msg.payload, 'ping')
        self.send_msg(message.Message(Header.PING, 'pong'))

        # Sending a incorrect pong to see server reaction
        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.PING)
        self.assertEqual(rcv_msg.payload, 'ping')

        self.send_msg(message.Message(Header.PING, 'ping'))
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
