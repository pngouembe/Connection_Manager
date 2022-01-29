import unittest
from com import Header, message, header_max


class TestComMethods(unittest.TestCase):

    msg_pattern = "{prefix}{header}{separator}{payload}{suffix}".format(
        prefix=message.prefix,
        header="{}",
        separator=message.separator,
        payload="{}",
        suffix=message.suffix)

    def test_generate(self):
        str = message.generate(Header.INTRODUCE, "Hello world!")
        exp_str = self.msg_pattern.format(Header.INTRODUCE.value, "Hello world!")
        self.assertEqual(str, exp_str)

        # Testing message generation with invalid payload
        with self.assertRaises(message.PayloadError):
            message.generate(Header.INTRODUCE,
                             "Hello {} world!".format(message.suffix))

        # Testing message generation with invalid header
        with self.assertRaises(ValueError):
            message.generate(Header(-1), "Hello world!")

    def test_decode(self):
        rcv_str = self.msg_pattern.format(
            Header.INTRODUCE.value, "Hello world!")
        msg_list = message.decode(rcv_str)
        exp_msg_list = [message.Message(Header.INTRODUCE, "Hello world!")]
        self.assertEqual(msg_list, exp_msg_list)

        # Testing multiple messages received at once
        rcv_str += self.msg_pattern.format(
            Header.END_CONNECTION.value, "Good bye!")
        msg_list = message.decode(rcv_str)
        exp_msg_list.append(message.Message(
            Header.END_CONNECTION, "Good bye!"))
        self.assertEqual(msg_list, exp_msg_list)

        # Testing special character payload decoding
        special_char_str = "special {} char".format(message.suffix)
        rcv_str += self.msg_pattern.format(Header.INVALID.value, special_char_str)
        msg_list = message.decode(rcv_str)
        exp_msg_list.append(message.Message(Header.INVALID, special_char_str))
        self.assertEqual(msg_list, exp_msg_list)

        # Testing no header
        rcv_str = self.msg_pattern.format('', "No header!")
        msg_list = message.decode(rcv_str)
        exp_msg_list = [message.Message(
            Header.INVALID, 'Received message incomplete, missing header or payload')]
        self.assertEqual(msg_list, exp_msg_list)

        rcv_str = b"$$$2|||name: Test client\naddress: 127.0.0.1\nresource: 0\n~~~"
        msg_list = message.decode(rcv_str)
        exp_msg_list = [message.Message(
            Header.INTRODUCE,
            'name: Test client\naddress: 127.0.0.1\nresource: 0\n')]
        self.assertEqual(msg_list, exp_msg_list)


if __name__ == '__main__':
    unittest.main()
