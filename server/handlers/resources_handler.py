import threading
from dataclasses import dataclass
from queue import Empty, Queue
from typing import List, Set, Union, Dict

from com import message
from com.header import Header
from mydataclasses.resources import Resource
from mylogger import clog
from users import User
from users.user import UserInfo

queue_timeout = 1
request_timout = 1


@dataclass
class ResourceRequest:
    user: User
    resource_ids: Set[int] = None

    def __post_init__(self):
        if not self.resource_ids:
            pass
        elif max(self.resource_ids) >= len(ResourceHandlerThread.resource_list):
            raise ValueError("Requested resource doesn't exist")
        # Event used for blocking requests
        self.handled: threading.Event = None


@dataclass
class ResourceRelease(ResourceRequest):
    pass


class ResourceHandlerThread(threading.Thread):
    """Thread responsible for the management of the server resources"""

    # Queue that contains the resource requests
    queue = None

    resource_list: List[Resource] = []
    # TODO:Check if it could be a set by using UserInfo __hash__() as User __hash__()
    user_dict: Dict[UserInfo, User] = {}

    def __init__(self, resource_list: List[Resource], run_event: threading.Event, request_queue: Queue) -> None:
        self.__class__.resource_list = resource_list
        self.run_event = run_event
        self.__class__.queue = request_queue
        super().__init__(name=self.__class__.__name__)

    @staticmethod
    def handle_request(request: Union[ResourceRequest, ResourceRelease], queue: Queue, blocks: bool = True) -> bool:
        if blocks:
            request.handled = threading.Event()
        queue.put(request)
        if blocks:
            return request.handled.wait(timeout=request_timout)
        else:
            return True

    def remove_user(self, users: Union[User, Set[User]]) -> bool:
        """Remove the users from the resources waiting list"""
        if not isinstance(users, set):
            users = {users}
        for user in users:
            r_list: Set[Resource] = user.requested_resources
            for r in r_list:
                r.remove_user(user)

        return True

    def notify_waiting_users(self, user: User):
        r_list: Set[Resource] = user.requested_resources
        for r in r_list:
            if r.user_list:
                if r.user_list[0] == user.info and len(r.user_list) > 1:
                    next_user = self.user_dict[r.user_list[1]]
                    msg_str = "Access to {}: {} granted to {}".format(
                        r.id, r.name, next_user.info.name)
                    msg = message.Message(Header.FREE_RESOURCE, msg_str)
                    message.send(next_user.socket, msg)

    def run(self):
        req: Union[ResourceRequest, ResourceRelease] = None
        while self.run_event.is_set():
            try:
                req = self.queue.get(timeout=queue_timeout)
            except Empty:
                continue

            if req.resource_ids:
                resources = [self.resource_list[id] for id in req.resource_ids]
            else:
                resources = self.resource_list

            if req.user.info not in self.user_dict.keys():
                self.user_dict[req.user.info] = req.user

            if req.__class__.__name__ == 'ResourceRelease':
                clog.info(f"removing {req.user} from resource list")
                self.notify_waiting_users(req.user)
                self.remove_user(req.user)
                del self.user_dict[req.user.info]

            else:
                free_resource_found = False
                for r in resources:
                    if r.is_free or r.user_list[0] == req.user.info:
                        # remove user from all waiting list
                        self.remove_user(req.user)

                        # add_user must be inside the if as it modifies is_free
                        r.add_user(req.user)
                        req.user.requested_resources = {r}
                        msg_header = Header.FREE_RESOURCE
                        msg_str = "Access to {}: {} granted to {}".format(
                            r.id, r.name, req.user.info.name)
                        msg = message.generate(msg_header, msg_str)
                        req.user.socket.send(msg.encode())
                        # First available resource access is granted and
                        # research is stopped
                        free_resource_found = True
                        break
                    else:
                        r.add_user(req.user)
                        req.user.requested_resources.update({r})

                if not free_resource_found:
                    msg_header = Header.WAIT
                    msg_str = "None of the requested resource is available"
                    msg = message.generate(msg_header, msg_str)
                    req.user.socket.send(msg.encode())

            # Notify that request handling is done if it was blocking
            if req.handled:
                req.handled.set()
