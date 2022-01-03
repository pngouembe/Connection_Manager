from dataclasses import dataclass, field, make_dataclass


class MissingRequiredFields(Exception):
    pass


@dataclass(frozen=True)
class Server:
    """
    Server dataclass allowing the storage of server information
    and the exchange of it between users
    """

    # list of the required fields
    address: str = field(hash=True)
    port: int = field(hash=True)


def server_from_dict(server_info: dict) -> Server:
    """
    This function allow to dynamically create user object as
    dataclasses with the fields given.
    """
    field_list = []
    for key, value in server_info.items():
        field_list.append((key, type(value), field()))
    try:
        return make_dataclass('Server', field_list, bases=(Server,), frozen=True)(**server_info)
    except TypeError:
        raise MissingRequiredFields(
            "Missing required fields in the given user info")
