from dataclasses import dataclass
from com import header, header_list
import re
from typing import List

separator = "|||"
prefix = "$$$"
suffix = "~~~"
pattern = r'((\${3}(?P<header>\d+)\|{3}(?P<payload>.*)~{3}))'


class PayloadError(Exception):
    pass


class HeaderError(Exception):
    pass


@dataclass
class Message:
    header: int
    payload: str


def generate(header, payload) -> str:
    if header not in header_list:
        raise HeaderError("Header {} is not known")
    elif suffix in payload:
        raise PayloadError(
            "Payload cannot contain following elements: {}".format(suffix))
    else:
        return prefix + str(header) + separator + str(payload) + suffix


def decode(msg: str) -> List[Message]:
    message_list = []
    for split_msg in msg.split(suffix + prefix):
        if not split_msg.endswith(suffix):
            split_msg += suffix
        if not split_msg.startswith(prefix):
            split_msg = prefix + split_msg
        m = re.search(pattern, split_msg)
        if m:
            tmp = m.groupdict()
            if int(tmp["header"]) not in header_list:
                tmp["header"] = header.INVALID
            tmp_msg = Message(int(tmp["header"]), tmp["payload"])
        else:
            tmp_msg = Message(
                header.INVALID,
                "Received message incomplete, missing header or payload")
        message_list.append(tmp_msg)
    return message_list


def ping():
    return generate(header.PING, 'ping')


def pong():
    return generate(header.PING, 'pong')
