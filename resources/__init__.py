# -*- coding: utf-8 -*-
"""Resource module
This module is made to define the resources that will be managed.
"""
from dataclasses import asdict, dataclass, field, make_dataclass
import yaml


@dataclass
class resource:
    """
    resource dataclass allowing the storage of resource information
    and the exchange of it between users
    """

    # list of the required fields
    name: str = field()
    id: int = field()
    user_list: list = field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    def __post_init__(self) -> None:
        pass

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


def create_resource(resource_info: dict) -> resource:
    """
    This function allow to dynamically create user object as
    dataclasses with the fields given.
    """
    field_list = []
    for key, value in resource_info.items():
        field_list.append((key, type(value), field()))
    return make_dataclass('resource', field_list, bases=(resource,))(**resource_info)
