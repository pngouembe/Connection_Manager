import unittest
from com import header, message, header_max


class TestComMethods(unittest.TestCase):

    msg_pattern = "{prefix}{header}{separator}{payload}{suffix}".format(
        prefix=message.prefix,
        header="{}",
        separator=message.separator,
        payload="{}",
        suffix=message.suffix)

    def test_generate(self):
        str = message.generate(header.INTRODUCE, "Hello world!")
        exp_str = self.msg_pattern.format(header.INTRODUCE, "Hello world!")
        self.assertEqual(str, exp_str)

        # Testing message generation with invalid payload
        with self.assertRaises(message.PayloadError):
            message.generate(header.INTRODUCE,
                             "Hello {} world!".format(message.suffix))

        # Testing message generation with invalid header
        with self.assertRaises(message.HeaderError):
            message.generate(-1, "Hello world!")

    def test_decode(self):
        rcv_str = self.msg_pattern.format(header.INTRODUCE, "Hello world!")
        msg_list = message.decode(rcv_str)
        exp_msg_list = [message.Message(header.INTRODUCE, "Hello world!")]
        self.assertEqual(msg_list, exp_msg_list)

        # Testing multiple messages received at once
        rcv_str += self.msg_pattern.format(header.END_CONNECTION, "Good bye!")
        msg_list = message.decode(rcv_str)
        exp_msg_list.append(message.Message(
            header.END_CONNECTION, "Good bye!"))
        self.assertEqual(msg_list, exp_msg_list)

        # Testing special character payload decoding
        special_char_str = "special {} char".format(message.suffix)
        rcv_str += self.msg_pattern.format(header_max + 1, special_char_str)
        msg_list = message.decode(rcv_str)
        exp_msg_list.append(message.Message(header.INVALID, special_char_str))
        self.assertEqual(msg_list, exp_msg_list)

        # Testing no header
        rcv_str = self.msg_pattern.format('', "No header!")
        msg_list = message.decode(rcv_str)
        exp_msg_list = [message.Message(
            header.INVALID, 'Received message incomplete, missing header or payload')]
        self.assertEqual(msg_list, exp_msg_list)

        rcv_str = b"$$$2|||name: Test client\naddress: 127.0.0.1\nresource: 0\n~~~"
        msg_list = message.decode(rcv_str)
        exp_msg_list = [message.Message(
            header.INTRODUCE,
            'name: Test client\naddress: 127.0.0.1\nresource: 0\n')]
        self.assertEqual(msg_list, exp_msg_list)
