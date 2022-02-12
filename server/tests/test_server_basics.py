import unittest
from com import message
from com.header import Header

import time

from server.tests import TestServerMethods


class TestServerConnectionMethods(TestServerMethods):
    def test_no_introduction(self):
        time.sleep(self.socket_timeout + .1)

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

        rcv_msg = self.recv_msg()
        self.assertEqual(rcv_msg.header, Header.END_CONNECTION)

    def test_send_end_connection(self):
        self.send_intro()

        self.send_end_connection()

if __name__ == '__main__':
    unittest.main()
