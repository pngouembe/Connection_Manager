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
        with self.assertRaises(message.payloadError):
            message.generate(header.INTRODUCE,
                             "Hello {} world!".format(message.suffix))

        # Testing message generation with invalid header
        with self.assertRaises(message.headerError):
            message.generate(-1, "Hello world!")

    def test_decode(self):
        rcv_str = self.msg_pattern.format(header.INTRODUCE, "Hello world!")
        msg_list = message.decode(rcv_str)
        exp_msg_list = [(header.INTRODUCE, "Hello world!")]
        self.assertEqual(msg_list, exp_msg_list)

        # Testing multiple messages received at once
        rcv_str += self.msg_pattern.format(header.END_CONNECTION, "Good bye!")
        msg_list = message.decode(rcv_str)
        exp_msg_list.append((header.END_CONNECTION, "Good bye!"))
        self.assertEqual(msg_list, exp_msg_list)

        # Testing invalid string decoding
        rcv_str += self.msg_pattern.format(header_max + 1, "Good {} bye!".format(message.suffix))
        msg_list = message.decode(rcv_str)
        exp_msg_list.append((header.INVALID, "Good "))
        self.assertEqual(msg_list, exp_msg_list)
