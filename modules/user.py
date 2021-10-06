#!/usr/bin/env python3

import threading
from json import loads, dumps
from typing import Any
from display import Logger

class User:
    __user_list = []
    __total_count = 0
    __active_count = 0
    
    lock = threading.Lock()
    __default_user_dict = {"name":"unknown", "comment":""}
    __default_user_private_dict = {"active_com":True}

    def __init__(self, user_info={}) -> None:
        self.user_info = User.__default_user_dict.copy()
        self.private_user_info = User.__default_user_private_dict.copy()
        self.user_info.update(user_info)
        User.__total_count += 1
        User.__active_count += 1
        self.private_user_info["id"]=User.__total_count
        User.lock.acquire()
        User.__user_list.append(self)
        User.lock.release()

    def __del__(self) -> None:
        User.__user_list.remove(self)
        User.__active_count -= 1

    def get_user_info(self, info_name: str) -> Any:
        ret = ''
        if info_name in self.user_info.keys():
            ret = self.user_info[info_name]
        elif info_name in self.private_user_info.keys():
            ret = self.private_user_info[info_name]
        return ret

    def get_user_name(self) -> str:
        return self.user_info["name"]

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
    def get_user_names_list() -> str:
        str = User.__user_list[0].get_user_name()
        for user in User.__user_list[1:]:
            str += ', ' + user.get_user_name()
        return str

    def update(self, dict) -> None:
        self.user_info.update(dict)

    def add_private_info(self, dict: dict) -> None:
        self.private_user_info.update(dict)

    def register_logger(self, logger: Logger) -> None:
        self.private_user_info.update({"user_logger": logger})

    def get_logger(self) -> Logger:
        return self.private_user_info["user_logger"]

    def update_from_json(self, data: str) -> None:
        self.user_info.update(loads(data))

    def json_dump(self) -> str:
        return dumps(self.user_info)

    def is_com_active(self) -> bool:
        return self.private_user_info["active_com"]
    
    def activate_com(self) -> None:
        self.private_user_info["active_com"] = True

    def desactivate_com(self) -> None:
        self.private_user_info["active_com"] = False

if __name__ == "__main__":
    u1 = User()
    print("User count : {}".format(User.get_user_count()))
    u2 = User({"name":"Pierre"})
    print("User count : {}".format(User.get_user_count()))
    u3 = User({"name":"Paul", "comment":"Jacques est pas loin"})
    print("User count : {}".format(User.get_user_count()))

    for key, value in User.get_user_list().items():
        print(key, value.user_info, sep=' :\n' )