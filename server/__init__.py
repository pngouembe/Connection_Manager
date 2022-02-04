import threading
from queue import Queue
from socket import (AF_INET, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, socket,
                    timeout)
from typing import Dict, List

from com import Header, message
from sdataclasses import MissingRequiredFields
from sdataclasses.servers import Server
from sdataclasses.uniquedataclass import DuplicateError
from users import User, UserInfo

from .handlers.clients_handler import ClientHandlerThread
from .handlers.resoures_handler import ResourceHandlerThread

socket_timeout = 1

def launch_server(server_config: Server):
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    bound = False
    while not bound:
        try:
            s.bind((server_config.address,
                    server_config.port))
            bound = True
            print("Successfully bound!")
        except OSError:
            print("Unable to bind")
            s.close()
            exit()

    s.listen(10)

    threads: list[ClientHandlerThread] = []
    str_2_user_info: Dict[str, UserInfo] = {}
    run_event = threading.Event()
    run_event.set()
    request_queue = Queue()
    t = ResourceHandlerThread(server_config.resources, run_event, request_queue)
    threads.append(t)
    t.start()
    while run_event.is_set():
        try:
            conn, addr = s.accept()
            conn.settimeout(socket_timeout)
        except KeyboardInterrupt:
            print("Ending Server Thread")
            run_event.clear()
            break
        try:
            data = conn.recv(1024)
        except timeout as e:
            msg_str = "Client introducing message not received, closing socket"
            print(msg_str)
            msg = message.generate(Header.END_CONNECTION, msg_str)
            conn.send(msg.encode())
            conn.close()
            continue
        msg_list: List[message.Message] = message.decode(data)
        for msg in msg_list:
            if msg.header == Header.INTRODUCE:
                try:
                    user_info = UserInfo.deserialize(str=msg.payload,
                                                     address=addr[0],
                                                     port=addr[1])
                except MissingRequiredFields as e:
                    err_msg = message.generate(Header.END_CONNECTION, e.message)
                    conn.send(err_msg.encode())
                    continue
                except DuplicateError:
                    user_info = str_2_user_info[msg.payload]
                finally:
                    user = User(info=user_info, socket=conn)

                t = ClientHandlerThread(user=user,
                                        run_event=run_event,
                                        request_queue=request_queue)

                threads.append(t)
                t.start()

    for t in threads:
        if t.is_alive():
            print("Waiting for {} Thread to end".format(t.name))
            t.join()
    s.close()
