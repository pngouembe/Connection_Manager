import threading
from queue import Queue
from socket import (AF_INET, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, socket,
                    timeout)
from typing import Dict, List

from com import message
from com.header import Header
from mydataclasses.sdataclasses import MissingRequiredFields
from mydataclasses.servers import Server
from mydataclasses.uniquedataclass import DuplicateError
from mylogger import clog
from myui.server.web import configure_app
from users import User, UserInfo

from server.handlers.clients_handler import ClientHandlerThread
from server.handlers.resources_handler import ResourceHandlerThread

debug_web = False


def launch_server(server_config: Server):

    app = configure_app(server_config)
    if debug_web:
        # TODO: Remove when web interface finished
        # TODO: Check why double ctrl+C is needed
        app.run(debug=True)
    else:
        # TODO: Use when web interface done
        t2 = threading.Thread(target=app.run, kwargs={
                              "debug": True, "use_reloader": False}).start()

    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    bound = False
    while not bound:
        try:
            s.bind((server_config.address,
                    server_config.port))
            bound = True
            clog.info("Successfully bound!")
        except OSError:
            clog.info("Unable to bind")
            s.close()
            exit()

    s.listen(10)

    threads: list[ClientHandlerThread] = []
    str_2_user: Dict[str, User] = {}
    run_event = threading.Event()
    run_event.set()
    request_queue = Queue()
    t = ResourceHandlerThread(server_config.resources,
                              run_event, request_queue)
    threads.append(t)
    t.start()

    while run_event.is_set():
        try:
            conn, addr = s.accept()
            conn.settimeout(server_config.socket_timeout)
        except KeyboardInterrupt:
            clog.info("Ending Server Thread")
            run_event.clear()
            break
        try:
            data = conn.recv(1024)
        except timeout as e:
            msg_str = "Client introducing message not received, closing socket"
            clog.info(msg_str)
            msg = message.generate(Header.END_CONNECTION, msg_str)
            conn.send(msg.encode())
            conn.close()
            continue
        msg_list: List[message.Message] = message.decode(data)
        for msg in msg_list:
            clog.info(msg)
            if msg.header == Header.INTRODUCE:
                try:
                    user_info = UserInfo.deserialize(msg.payload)
                except MissingRequiredFields as e:
                    err_msg = message.generate(
                        Header.END_CONNECTION, e.message)
                    conn.send(err_msg.encode())
                    continue
                except DuplicateError:
                    """
                    TODO: debug use following use case:
                    User connects once, use try to connect
                    """
                    user = str_2_user[msg.payload]
                    if user.waiting_for_reconnection:
                        user.socket.close()
                        user.socket = conn
                        user.reconnection_event.set()
                    else:
                        err_msg = message.generate(
                            Header.END_CONNECTION, "User already connected")
                        conn.send(err_msg.encode())
                else:
                    user = User(info=user_info,
                                socket=conn,
                                recovery_time=server_config.resource_free_delay)

                    str_2_user[msg.payload] = user

                    t = ClientHandlerThread(user=user,
                                            run_event=run_event,
                                            request_queue=request_queue)

                    threads.append(t)
                    t.start()

    for t in threads:
        if t.is_alive():
            # TODO: Send end connection to alive clients
            clog.info("Waiting for {} Thread to end".format(t.name))
            t.join()
    s.close()
