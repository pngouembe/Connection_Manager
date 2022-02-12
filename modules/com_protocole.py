#!/usr/bin/env python3

import re
from enum import Enum, unique
from typing import Any, Tuple

from mylogger import log


@unique
class ComHeaders(Enum):
    INVALID=0
    END_CONNECTION=1
    INTRODUCE=2
    WAIT=3
    FREE_RESOURCE=4
    TIMEOUT=5
    UPDATE=6
    def __str__(self) -> str:
        return str(self.value)

class ComProtocole:
    __separator = "|||"
    __prefix = "$$$"
    __sufix = "~~~"
    __pattern = r'(\$\$\$(?P<header>\d+)\|\|\|(?P<payload>[^\~]*)\~\~\~)'

    @classmethod
    def generate_msg(cls, header: ComHeaders, payload: Any = '') -> str :
        return cls.__prefix + str(header) + cls.__separator + str(payload) + cls.__sufix

    @classmethod
    def decode_msg(cls, msg: str) -> list:
        message_list = []
        header = ComHeaders.INVALID.value
        payload = ''
        if msg != '':
            for m in re.finditer(cls.__pattern, msg):
                tmp = m.groupdict()
                message_list.append((ComHeaders(int(tmp["header"])), tmp["payload"]))
        else:
            message_list.append((ComHeaders(int(header)), payload))
        return message_list

if __name__ == "__main__":
    msg = ComProtocole.generate_msg(ComHeaders.END_CONNECTION)
    log.info(msg)
    dec_msg = ComProtocole.decode_msg(msg)
    log.info(dec_msg, end="\n\n")
    msg2 = ComProtocole.generate_msg(ComHeaders.INTRODUCE, "coucou c'est moi")
    log.info(msg2)
    dec_msg2 = ComProtocole.decode_msg(msg2)
    log.info(dec_msg2, end="\n\n")
