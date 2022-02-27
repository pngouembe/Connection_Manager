import re
from dataclasses import dataclass, field
from datetime import datetime
from socket import socket
from typing import List, Union

from mylogger import clog
from rich.pretty import Pretty

from com.header import Header

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
    elif suffix in str(payload):
        raise PayloadError(
            "Payload cannot contain following elements: {}".format(suffix))
    else:
        return prefix + str(header.value) + separator + str(payload) + suffix


@dataclass
class Message:
    header: Header
    payload: str
    timestamp: str = field(default="")

    def __rich__(self):
        return Pretty(self)

    def __post_init__(self):
        self.timestamp = datetime.now().strftime("%H:%M:%S")

    # def __repr__(self) -> str:
    #     return f"[{self.timestamp}] {self.header.name} - {self.payload}"

    def __rich_repr__(self):
        yield self.timestamp
        yield "header", self.header.name
        yield "payload", self.payload

    def encode(self) -> bytes:
        return generate(self.header, self.payload).encode()

    # TODO: Add send method


# TODO: Use everywhere
def send(sock: socket, msg: Message):
    clog.debug(f"Send: {msg}")
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

# TODO: Use everywhere


def recv(sock: socket) -> List[Message]:
    msg_list = decode(sock.recv(1024))
    for msg in msg_list:
        clog.debug(f"Recv: {msg}")
    return msg_list


ping = Message(Header.PING, "ping")
pong = Message(Header.PING, "pong")
