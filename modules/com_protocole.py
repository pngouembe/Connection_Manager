#!/usr/bin/env python3

from enum import Enum, unique
from typing import Any, Tuple

@unique
class ComHeaders(Enum):
    END_CONNECTION=0
    INTRODUCE=1
    WAIT=2
    FREE_RESOURCE=3
    def __str__(self) -> str:
        return str(self.value)

class ComProtocole:
    __separator = "|||"

    @classmethod
    def generate_msg(cls, header: ComHeaders, payload: Any = '') -> str :
        return str(header) + cls.__separator + str(payload)

    @classmethod
    def decode_msg(cls, msg: str) -> Tuple[ComHeaders, str]:
        header, payload = msg.split(cls.__separator)
        return (ComHeaders(int(header)), payload)

if __name__ == "__main__":
    msg = ComProtocole.generate_msg(ComHeaders.END_CONNECTION)
    print(msg)
    dec_msg = ComProtocole.decode_msg(msg)
    print(dec_msg, end="\n\n")
    msg2 = ComProtocole.generate_msg(ComHeaders.INTRODUCE, "coucou c'est moi")
    print(msg2)
    dec_msg2 = ComProtocole.decode_msg(msg2)
    print(dec_msg2, end="\n\n")
    
