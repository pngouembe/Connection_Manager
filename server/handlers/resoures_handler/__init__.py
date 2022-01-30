from queue import Empty, Queue
import threading
from socket import socket, timeout
from typing import Dict, List, Set, Union
from dataclasses import dataclass, field
from flask import request

from com import Header, message
from sdataclasses.resources import Resource
from sdataclasses.uniquedataclass.users import User

queue_timeout = 1
request_timout = 1


@dataclass
class ResourceRequest:
    user: User
    user_sock: socket = field(repr=False)
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


@dataclass
class UserData:
    """Class used to centralize user related elements

    Attributes:
        user_sock:              Socket used to communicate with the user
        requested_resources:    List of resource requested by the user
    """
    user_sock: socket
    requested_resources: Set[Resource] = field(default_factory=set)

    def update_resources(self, requested_resources: Set[Resource]):
        self.requested_resources.update(requested_resources)


class ResourceHandlerThread(threading.Thread):
    """Thread responsible for the management of the server resources"""

    # Queue that contains the resource requests
    queue = None

    resource_list: List[Resource] = []

    # Dictionnary that maps user to their userData
    user_data_map: Dict[User, UserData] = {}

    def __init__(self, resource_list: List[Resource], run_event: threading.Event, request_queue: Queue) -> None:
        self.__class__.resource_list = resource_list
        self.run_event = run_event
        self.__class__.queue = request_queue
        super().__init__(name=self.__class__.__name__)

    @staticmethod
    def handle_request(request: Union[ResourceRequest, ResourceRelease], queue: Queue, blocks: bool = True) -> bool:
        if blocks:
            e = threading.Event()
            e.clear()
            request.handled = e
        queue.put(request)
        if blocks:
            return request.handled.wait(timeout=request_timout)
        else:
            return True

    def get_used_resources(self, user: User) -> Set[Resource]:
        """Return resources requested by a user"""
        try:
            return self.user_data_map[user].requested_resources
        except KeyError:
            # User never requested any resource
            return set()

    def remove_user(self, users: Union[User, Set[User]]) -> bool:
        """Remove the users from the resources waiting list"""
        if not isinstance(users, set):
            users = {users}
        for user in users:
            r_list = self.get_used_resources(user)
            for r in r_list:
                r.remove_user(user)

            try:
                del self.user_data_map[user]
            except KeyError:
                # User never requested any resource
                pass
        return True

    def notify_waiting_users(self, user: User):
        r_list = self.get_used_resources(user)
        for r in r_list:
            if r.user_list[0] == user and len(r.user_list) > 1:
                next_user = r.user_list[1]
                next_user_sock = self.user_data_map[next_user].user_sock
                msg_str = "Access to {}: {} granted".format(r.id, r.name)
                msg = message.Message(Header.FREE_RESOURCE, msg_str)
                message.send(next_user_sock, msg)


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
            u_hash = hash(req.user)
            if req.__class__.__name__ == 'ResourceRelease':
                print(f"removing {req.user} from resource list")
                self.notify_waiting_users(req.user)
                self.remove_user(req.user)
            else:
                free_resource_found = False
                for i, r in enumerate(resources):
                    if r.is_free:
                        # remove user from all waiting list
                        self.remove_user(req.user)

                        # add_user must be inside the if as it modifies is_free
                        r.add_user(req.user)
                        user_data = UserData(req.user_sock, {r})
                        self.user_data_map[req.user] = user_data
                        msg_header = Header.FREE_RESOURCE
                        msg_str = "Access to {}: {} granted".format(
                            r.id, r.name)
                        msg = message.generate(msg_header, msg_str)
                        req.user_sock.send(msg.encode())
                        # First available resource access is granted and
                        # research is stopped
                        free_resource_found = True
                        break
                    else:
                        r.add_user(req.user)
                        try:
                            self.user_data_map[req.user].update_resources({r})
                        except KeyError:
                            user_data = UserData(req.user_sock, {r})
                            self.user_data_map[req.user] = user_data

                if not free_resource_found:
                    msg_header = Header.WAIT
                    msg_str = "None of the requested resource is available"
                    msg = message.generate(msg_header, msg_str)
                    req.user_sock.send(msg.encode())

            # Notify that request handling is done if it was blocking
            if req.handled:
                req.handled.set()
