#!/usr/bin/env python3

import threading

class User:
    __user_list = {}
    __total_count = 0
    __active_count = 0
    
    lock = threading.Lock()
    __default_user_dict = {"name":"unknown", "comment":""}

    def __init__(self, user_info={}) -> None:
        self.user_info = User.__default_user_dict.copy()
        self.user_info.update(user_info)
        User.__total_count += 1
        User.__active_count += 1
        self.user_info["id"]=User.__total_count
        User.lock.acquire()
        User.__user_list[User.__total_count] = self
        User.lock.release()

    def __del__(self) -> None:
        print("del")
        User.__active_count -= 1

    def get_user_name(self) -> str:
        return self.user_info["name"]
    @staticmethod
    def get_user_count() -> int:
        return User.__active_count
    @staticmethod
    def get_total_user_count() -> int:
        return User.__active_count
    
    @staticmethod
    def get_user_list() -> list:
        return User.__user_list

    def update(self, dict) -> None:
        self.user_info.update(dict)
    

if __name__ == "__main__":
    u1 = User()
    print("User count : {}".format(User.get_user_count()))
    u2 = User({"name":"Pierre"})
    print("User count : {}".format(User.get_user_count()))
    u3 = User({"name":"Paul", "comment":"Jacques est pas loin"})
    print("User count : {}".format(User.get_user_count()))

    for key, value in User.get_user_list().items():
        print(key, value.user_info, sep=' :\n' )