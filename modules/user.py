#!/usr/bin/env python3

import threading
from json import loads, dumps
from typing import Any
from display import Logger
from resource_mgr import Resource, ResourceMgr

class User:
    __user_list = []
    __resource_list = ResourceMgr()
    __total_count = 0
    __active_count = 0

    lock = threading.Lock()
    __default_user_dict = {"name":"unknown", "comment":"", "timeout":0, "start_time":0}
    __default_user_private_dict = {
        "active_com": True, "duplicate": False, "timed_out": False}

    def __init__(self, user_info={}, add_to_list:bool=True) -> None:
        self.__user_info = User.__default_user_dict.copy()
        self.__private_user_info = User.__default_user_private_dict.copy()
        self.__user_info.update(user_info)
        if add_to_list:
            User.__total_count += 1
            User.__active_count += 1
            self.__private_user_info["id"]=User.__total_count
            User.lock.acquire()
            User.__user_list.append(self)
            User.lock.release()

    def __del__(self, duplicate=False) -> None:
        if self in User.__user_list:
            User.__user_list.remove(self)
        User.__active_count -= 1

    def remove_from_list(self):
        if self in User.__user_list:
            User.__user_list.remove(self)


    def get_user_info(self, info_name: str) -> Any:
        ret = ''
        if info_name in self.__user_info.keys():
            ret = self.__user_info[info_name]
        elif info_name in self.__private_user_info.keys():
            ret = self.__private_user_info[info_name]
        return ret

    def get_user_name(self) -> str:
        return self.__user_info["name"]

    def get_user_comment(self) -> str:
        return self.__user_info["comment"]

    def get_user_id(self) -> str:
        return self.__private_user_info["id"]

    @staticmethod
    def get_user_count() -> int:
        return User.__active_count

    @staticmethod
    def get_total_user_count() -> int:
        return User.__total_count

    @staticmethod
    def get_user_list() -> list:
        return User.__user_list

    @staticmethod
    def get_first_user_in_line():
        return User.__user_list[0]

    @staticmethod
    def get_next_user_in_line(user):
        idx = User.__user_list.index(user)
        return User.__user_list[idx + 1]

    @staticmethod
    def set_next_user_in_line(user):
        idx = User.__user_list.index(user)
        User.__user_list.insert(1, User.__user_list.pop(idx))

    @staticmethod
    def get_user_reconnexion_attempt(user):
        idx = User.__user_list.index(user)
        for u in User.__user_list[idx+1:]:
            if u.get_user_name() == user.get_user_name():
                return u

    @staticmethod
    def get_user_names_list() -> str:
        str = ''
        if len(User.__user_list) >= 1:
            str = User.__user_list[0].get_user_name()
            if len(User.__user_list) > 1:
                for user in User.__user_list[1:]:
                    str += ', ' + user.get_user_name()
        return str

    @staticmethod
    def get_waiting_list() -> str:
        str = User.__user_list[1].get_user_name()
        for user in User.__user_list[2:]:
            str += ', ' + user.get_user_name()
        return str

    def update(self, dict) -> None:
        self.__user_info.update(dict)

    def add_private_info(self, dict: dict) -> None:
        self.__private_user_info.update(dict)

    def register_logger(self, logger: Logger) -> None:
        self.__private_user_info.update({"user_logger": logger})

    def get_logger(self) -> Logger:
        return self.__private_user_info["user_logger"]

    def update_from_json(self, data: str) -> None:
        self.__user_info.update(loads(data))

    def json_dump(self) -> str:
        return dumps(self.__user_info)

    def get_user_info_dict(self) -> dict:
        return self.__user_info

    def get_user_private_info_dict(self) -> dict:
        return self.__private_user_info

    def is_com_active(self) -> bool:
        return self.__private_user_info["active_com"]

    def is_duplicate(self) -> bool:
        return self.__private_user_info["duplicate"]

    def is_trying_to_reconnect(self) -> bool:
        # TODO Found a better way to detect reconnections
        # ret = False
        # if len(User.get_user_list()) > 2:
        #     waiting_list = User.get_waiting_list()
        #     ret = self.get_user_name() in waiting_list
        # return ret
        return User.get_user_names_list().count(self.get_user_name()) > 1

    def is_timed_out(self) -> bool:
        return self.__private_user_info["timed_out"]

    def activate_com(self) -> None:
        self.__private_user_info["active_com"] = True

    def desactivate_com(self) -> None:
        self.__private_user_info["active_com"] = False

    def set_as_duplicate(self) -> None:
        self.__private_user_info["duplicate"] = True

    def timed_out(self) -> None:
        self.__private_user_info["timed_out"] = True

    def get_resource(self) -> Resource:
        id = self.__user_info["resource"]
        return User.__resource_list.get_resource_by_id(id)

    def is_next_in_line(self) -> bool:
        resource = self.get_resource()
        if resource.waiting_list != []:
            return resource.get_first_user_in_line() == self
        else:
            self.add_to_resource_waiting_list()
            return True

    def init_resources(self, resources):
        for r in resources:
            User.__resource_list.add_resource(Resource(r["name"], r["info"]))

    def add_to_resource_waiting_list(self):
        resource = self.get_resource()
        resource.get_resource(self)

    def remove_from_resource_waiting_list(self):
        resource = self.get_resource()
        resource.free_resource(self)


if __name__ == "__main__":
    u1 = User()
    print("User count : {}".format(User.get_user_count()))
    u2 = User({"name":"Pierre"})
    print("User count : {}".format(User.get_user_count()))
    u3 = User({"name":"Paul", "comment":"Jacques est pas loin"})
    print("User count : {}".format(User.get_user_count()))

    for key, value in User.get_user_list().items():
        print(key, value.__user_info, sep=' :\n' )
