#!/usr/bin/env python3

class Resource:
    __resource_nb = 0

    def __init__(self, name="resource#", info=None) -> None:
        self.id = Resource.__resource_nb
        Resource.__resource_nb += 1
        self.name = name if name != "resource#" else name + str(self.id)
        self.is_free = True
        self.waiting_list = []
        self.info = info

    def __add_user_to_waiting_list(self, user) -> None:
        self.waiting_list.append(user)

    def get_first_user_in_line(self):
        return self.waiting_list[0]

    def get_next_user_in_line(self, user):
        idx = self.waiting_list.index(user)
        return self.waiting_list[idx + 1]

    def __remove_user_from_line(self, user):
        self.waiting_list.remove(user)

    def get_resource(self, user) -> None:
        self.is_free = False
        self.__add_user_to_waiting_list(user)

    def free_resource(self, user) -> None:
        self.__remove_user_from_line(user)
        self.is_free = True


class ResourceMgr:
    def __init__(self, resource_list=[]) -> None:
        self.resource_list: list = resource_list

    def add_resource(self, resource: Resource) -> None:
        self.resource_list.append(resource)

    def get_resource_by_id(self, id):
        return self.resource_list[id]

    def add_user(self, user, resource_id) -> None:
        self.resource_list[resource_id].__add_user_to_waiting_list(user)
