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


class ResourceHandlerThread(threading.Thread):
    """
    Queue that contains the resource requests
    """
    queue = None
    resource_list: List[Resource] = []
    u2r_map: Dict[User, set] = {}

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

    def remove_user(self, user: Union[User, Set[User]]) -> bool:
        if not isinstance(user, set):
            user = {user}
        for u in user:
            u_hash = hash(u)
            if u_hash in self.u2r_map.keys():
                for i in self.u2r_map[u_hash]:
                    self.resource_list[i].remove_user(u)

                del self.u2r_map[u_hash]
        return True

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
                self.remove_user(req.user)
            else:
                free_resource_found = False
                for i, r in enumerate(resources):
                    if r.is_free:
                        # remove user from all waiting list
                        self.remove_user(req.user)

                        # add_user must be inside the if as it modifies is_free
                        r.add_user(req.user)
                        self.u2r_map[u_hash] = {i}
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
                        if u_hash not in self.u2r_map.keys():
                            self.u2r_map[u_hash] = {i}
                        else:
                            self.u2r_map[u_hash].union({i})

                if not free_resource_found:
                    msg_header = Header.WAIT
                    msg_str = "None of the requested resource is available"
                    msg = message.generate(msg_header, msg_str)
                    req.user_sock.send(msg.encode())

            # Notify that request handling is done if it was blocking
            if req.handled:
                req.handled.set()
