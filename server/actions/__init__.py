
from com import header, header_list
from sdataclasses.uniquedataclass.users import User

action_list = []


def pass_fct(*args, **kwargs):
    pass


for i in header_list:
    action_list.append(pass_fct)


def action(com_header: header):
    global action_list

    def wrap(func):
        action_list[com_header] = func
    return wrap


@action(header.INVALID)
def invalid_handling():
    pass_fct()
    return False


def handle(user: User, com_header: header, payload: str) -> bool:
    """
    Execute the registered action for the message type received.
    Return True if the handling was successful otherwise return False
    """
    return action_list[com_header](user, payload)
