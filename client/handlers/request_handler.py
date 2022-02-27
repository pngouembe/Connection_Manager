import threading
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Dict, List, Set, Union

from com import message
from com.header import Header
from mydataclasses.resources import Resource
from mylogger import clog
from users import User, user
from users.user import UserInfo

# TODO: Make common with server

# TODO: Make configurable
queue_timeout = 1
request_timout = 1

# TODO: Transform request into send actions


@dataclass
class ResourceRequest:
    user: User
    resource_ids: Set[int] = None

    def __post_init__(self):
        # Event used for blocking requests
        self.handled: threading.Event = None


@dataclass
class ResourceRelease(ResourceRequest):
    pass


class RequestHandlerThread(threading.Thread):
    """Thread responsible for the management of the server resources"""

    def __init__(self, run_event: threading.Event, request_queue: Queue, read_queue: Queue) -> None:
        self.run_event = run_event
        self.request_queue = request_queue
        self.read_queue = read_queue
        super().__init__(name=self.__class__.__name__)

    def handle_request(self, request: Union[ResourceRequest, ResourceRelease], blocks: bool = True) -> bool:
        if blocks:
            request.handled = threading.Event()
        self.request_queue.put(request)
        if blocks:
            return request.handled.wait(timeout=request_timout)
        else:
            return True

    # TODO: use send actions instead of requests
    def run(self):
        req: Union[ResourceRequest, ResourceRelease] = None
        while self.run_event.is_set():
            try:
                req = self.request_queue.get(timeout=queue_timeout)
            except Empty:
                continue
            else:
                clog.info(f"Received following request {req}")

            if req.__class__.__name__ == 'ResourceRelease':
                clog.info(
                    f"Releasing resources {req.user.current_resource}")
                msg = message.Message(Header.RELEASE_RESOURCE, "")
                msg.send(req.user.socket)

                msg: message.Message = self.read_queue.get()
                if msg.header == Header.RELEASE_RESOURCE:
                    clog.info(f"Resource freed successfully")
                else:
                    clog.info(f"Unexpected response to free resource message")

            else:
                clog.info(
                    f"Requesting resources: {req.user.requested_resources}")
                msg = message.Message(
                    Header.REQUEST_RESOURCE,
                    ",".join(req.user.requested_resources)
                )
                msg.send(req.user.socket)

                msg: message.Message = self.read_queue.get()
                if msg.header == Header.FREE_RESOURCE:
                    clog.info(f"Resource {msg.payload} requested successfully")
                else:
                    clog.info(f"No resource available")

            # Request current server status after each request
            msg = message.Message(
                Header.STATUS,
                ",".join(req.user.requested_resources)
            )
            message.send(req.user.socket, msg)

            # Notify that request handling is done if it was blocking
            if req.handled:
                req.handled.set()
