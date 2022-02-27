
import threading
from queue import Queue
from socket import AF_INET, SOCK_STREAM, gethostbyname, socket, timeout
from typing import Dict

from com import message
from com.header import Header
from mydataclasses.sdataclasses import MissingRequiredFields
from mydataclasses.uniquedataclass import DuplicateError
from mylogger import clog
from myui.client.teminal import ClientTerminalDashboard
from myui.client.web import configure_app
from users import User, UserInfo

from client.handlers.com_handler import ClientComThread
from client.handlers.request_handler import RequestHandlerThread

debug_web = False
# TODO: Make configurable
client_socket_timeout = 1


class ServerNotReadyError(Exception):
    def __init__(self, *args: object) -> None:
        clog.info("Server not ready, unable to communicate")
        super().__init__(*args)


def launch_client(client_dict: Dict):
    if "address" not in client_dict.keys():
        raise MissingRequiredFields("address")

    client_dict["address"] = gethostbyname(client_dict["address"])
    user_info = UserInfo(**client_dict)
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(client_socket_timeout)
    s.connect((user_info.address, user_info.port))
    user = User(info=user_info, socket=s)
    run_event = threading.Event()
    run_event.set()
    request_queue = Queue()
    read_queue = Queue()

    com_thread = ClientComThread(
        user=user, run_event=run_event, queue=read_queue)
    request_thread = RequestHandlerThread(
        run_event=run_event, request_queue=request_queue, read_queue=read_queue)
    request_thread.start()
    app = configure_app(user, request_thread=request_thread)

    # TODO: Use actions for that
    # Checking server availability
    msg = message.Message(Header.INTRODUCE, user.info.serialize())
    message.send(user.socket, msg)
    try:
        msg_list = message.recv(user.socket)
    except timeout:
        raise ServerNotReadyError(
            f"No message received after waiting {client_socket_timeout}s")
    if msg_list[0].header == Header.END_CONNECTION:
        clog.error(msg_list[0])
        raise DuplicateError("Client already running")
    elif msg_list[0].header != Header.CONNECTION_READY:
        raise ServerNotReadyError(msg_list[0])

    com_thread.start()

    msg = message.Message(
        Header.STATUS,
        ",".join(user.requested_resources)
    )
    message.send(user.socket, msg)

    if debug_web == None:
        pass
    elif debug_web == True:
        # TODO: Remove when web interface finished
        # TODO: Check why double ctrl+C is needed
        app.run(debug=True, port=5001)
    else:
        # TODO: Use when web interface done
        t3 = threading.Thread(target=app.run,
                              kwargs={
                                  "debug": True,
                                  "use_reloader": False,
                                  "port": 5001},
                              daemon=True).start()

    # t2 = ClientTerminalDashboard(
    #     user=user, run_event=run_event, queue=read_queue
    # )
    # t2.start()

    try:
        com_thread.join()
        # t2.join()
    except KeyboardInterrupt:
        run_event.clear()
        com_thread.join()
        # t2.join()
