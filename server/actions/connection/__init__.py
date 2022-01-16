from actions import action, invalid_handling
from com import header, message
from sdataclasses.uniquedataclass.users import User


@action(header.END_CONNECTION)
def end_connection_handling(user: User, payload: str) -> bool:
    pass


@action(header.INTRODUCE)
def introduction_handling(user: User, payload: str) -> bool:
    # User are introduce once and before launching the client handler thread
    return invalid_handling()


@action(header.PING)
def ping_handling(user: User, payload: str) -> bool:
    if 'pong' == payload:
        return True
    else:
        print("Client response to ping is incorrect")
        return False
