# -*- coding: utf-8 -*-
"""Resource module
This module is made to define the resources that will be managed.
"""
from dataclasses import asdict, dataclass, field, make_dataclass
import yaml


class MissingRequiredFields(Exception):
    pass


@dataclass
class Resource:
    """
    resource dataclass allowing the storage of resource information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field()
    id: int = field()
    user_list: list = field(default_factory=list)
    is_usable: bool = field(default=True)

    def __post_init__(self) -> None:
        self.is_free = True

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

    def add_user(self, user) -> None:
        """
        Add user given in argument to the resource user waiting list
        """
        self.user_list.append(user)
        self.is_free = False

    def remove_user(self, user) -> None:
        """
        Remove the user given in argument from the resource user waiting list
        """
        self.user_list.remove(user)
        if not self.user_list:
            self.is_free = True


def resource_from_dict(resource_info: dict) -> Resource:
    """
    This function allow to dynamically create user object as
    dataclasses with the fields given.
    """
    field_list = []
    for key, value in resource_info.items():
        field_list.append((key, type(value), field()))
    try:
        return make_dataclass('resource', field_list, bases=(Resource,))(**resource_info)
    except TypeError:
        raise MissingRequiredFields(
            "Missing required fields in the given user info")
