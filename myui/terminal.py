import threading
from queue import Queue

from users import User


class TerminalDashboard(threading.Thread):
    def __init__(self, user: User, run_event: threading.Event, queue: Queue) -> None:
        self.user = user
        self.run_event = run_event
        self.queue = queue
        super().__init__(name=user.info.name)
