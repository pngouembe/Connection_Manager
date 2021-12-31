from com import header, header_list
import re

separator = "|||"
prefix = "$$$"
suffix = "~~~"
pattern = r'((\${3}(?P<header>\d+)\|{3}(?P<payload>[^~{3}]+)~{3}))'


class payloadError(Exception):
    pass


class headerError(Exception):
    pass

def generate(header, payload) -> str:
    if header not in header_list:
        raise headerError("Header {} is not known")
    elif suffix in payload:
        raise payloadError(
            "Payload cannot contain following elements: {}".format(suffix))
    else:
        return prefix + str(header) + separator + str(payload) + suffix


def decode(msg: str) -> list:
    message_list = []
    for m in re.finditer(pattern, msg):
        tmp = m.groupdict()
        if int(tmp["header"]) not in header_list:
            tmp["header"] = header.INVALID
        message_list.append((int(tmp["header"]), tmp["payload"]))
    return message_list
