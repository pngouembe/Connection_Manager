from socket import socket, timeout
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import threading
from users import User
from .dataclass import Server
from .handlers import ClientHandlerThread
from com import header, message

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
    run_event = threading.Event()
    run_event.set()
    while run_event:
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
            print("Client introducing message not received, closing socket")
            conn.close()
            continue
        msg_list: message.Message = message.decode(data)
        for msg in msg_list:
            if msg.header == header.INTRODUCE:
                user = User.deserialize(
                    msg.payload, address=addr[0], port=addr[1])
                threads.append(ClientHandlerThread(
                    client_data=user, client_socket=conn, run_event=run_event))
                threads[-1].start()
    for t in threads:
        if t.is_alive():
            print("Waiting for {} Thread to end".format(t.name))
            t.join()
    s.close()
