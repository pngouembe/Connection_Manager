# -*- coding: utf-8 -*-
"""User module
This module is made to define what connection manage users can do and the
information linked to them.
"""
from dataclasses import asdict, dataclass, field, make_dataclass
import yaml


class userDuplicateError(Exception):
    pass


@dataclass(frozen=True)
class user:
    """
    User dataclass allowing the storage of user information
    and the exchange of it between users
    """

    users_ids = []

    # list of the required fields
    name: str = field(hash=True)
    ip_addr: str = field(hash=True)
    resource: int = field(default=0, hash=True)

    def __post_init__(self) -> None:
        """
        The post init method is used to check the unicity of the user.
        it raises an error if the user is a duplicate
        """
        if self.__hash__() not in user.users_ids:
            user.users_ids.append(self.__hash__())
        else:
            raise userDuplicateError("Duplication of users is not allowed")

    def serialize(self) -> str:
        """
        Function used to generate a yaml string from the user data.
        It make it easier to send this information to other user
        """
        return yaml.dump(asdict(self), sort_keys=False)

    def update(self, str) -> None:
        """
        Function used to update user information from a yaml string.
        """
        self.__dict__.update(yaml.safe_load(str))


def create_user(user_info: dict) -> user:
    """
    This function allow to dynamically create user object as
    dataclasses with the fields given.
    """
    field_list = []
    for key, value in user_info.items():
        field_list.append((key, type(value), field()))
    return make_dataclass('user', field_list, bases=(user,), frozen=True)(**user_info)
