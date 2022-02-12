
from queue import Queue
from socket import AF_INET, SOCK_STREAM, gethostbyname, socket
import threading
from typing import Dict

from mydataclasses.sdataclasses import MissingRequiredFields
from users import UserInfo, User
from client.handlers.com_handler import ComThread


def launch_client(client_dict: Dict):
    if "address" not in client_dict.keys():
        raise MissingRequiredFields("address")

    client_dict["address"] = gethostbyname(client_dict["address"])
    user_info = UserInfo(**client_dict)
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((user_info.address, user_info.port))
    user = User(info=user_info, socket=s)

    run_event = threading.Event()
    run_event.set()
    read_queue = Queue()
    t = ComThread(user=user, run_event=run_event, read_queue=read_queue)
    t.start()

    try:
        t.join()
    except KeyboardInterrupt:
        run_event.clear()
        t.join()
