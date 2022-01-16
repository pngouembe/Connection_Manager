from actions import action
from com import header
from sdataclasses.uniquedataclass.users import User


@action(header.FREE_RESOURCE)
def free_resource_handling(user: User, payload: str) -> bool:
    pass


@action(header.INVALID)
def invalid_handling(user: User, payload: str) -> bool:
    pass


@action(header.TIMEOUT)
def timeout_handling(user: User, payload: str) -> bool:
    pass


@action(header.UPDATE)
def update_handling(user: User, payload: str) -> bool:
    pass


@action(header.WAIT)
def update_handling(user: User, payload: str) -> bool:
    pass
