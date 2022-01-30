from dataclasses import dataclass
from com import Header, header_list
import re
from typing import List, Union
from socket import socket

separator = "|||"
prefix = "$$$"
suffix = "~~~"
pattern = r'((\${3}(?P<header>\d+)\|{3}(?P<payload>[\s\S]*)~{3}))'


class PayloadError(Exception):
    pass


class HeaderError(Exception):
    pass

def generate(header: Header, payload) -> str:
    if header.value not in [e.value for e in Header]:
        raise HeaderError("Header {} is not known")
    elif suffix in payload:
        raise PayloadError(
            "Payload cannot contain following elements: {}".format(suffix))
    else:
        return prefix + str(header.value) + separator + str(payload) + suffix

@dataclass
class Message:
    header: Header
    payload: str

    def encode(self) -> bytes:
        return generate(self.header, self.payload).encode()


def send(sock: socket, msg: Message):
    sock.send(msg.encode())


def decode(msg: Union[str, bytes]) -> List[Message]:
    message_list = []
    if isinstance(msg, bytes):
        msg = msg.decode(encoding='raw_unicode_escape')

    for split_msg in msg.split(suffix + prefix):
        if not split_msg.endswith(suffix):
            split_msg += suffix
        if not split_msg.startswith(prefix):
            split_msg = prefix + split_msg
        m = re.search(pattern, split_msg)
        if m:
            tmp = m.groupdict()
            if int(tmp["header"]) not in [e.value for e in Header]:
                tmp["header"] = Header.INVALID.value
            tmp_msg = Message(Header(int(tmp["header"])), tmp["payload"])
        else:
            tmp_msg = Message(
                Header.INVALID,
                "Received message incomplete, missing header or payload")
        message_list.append(tmp_msg)
    return message_list


def ping():
    return generate(Header.PING, 'ping')


def pong():
    return generate(Header.PING, 'pong')
