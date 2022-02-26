
from queue import Queue
from socket import AF_INET, SOCK_STREAM, gethostbyname, socket
import threading
from typing import Dict

from mydataclasses.sdataclasses import MissingRequiredFields
from users import UserInfo, User
from client.handlers.com_handler import ComThread
from myui.client.teminal import ClientTerminalDashboard
from myui.client.web import configure_app

debug_web = False

def launch_client(client_dict: Dict):
    if "address" not in client_dict.keys():
        raise MissingRequiredFields("address")

    client_dict["address"] = gethostbyname(client_dict["address"])
    user_info = UserInfo(**client_dict)
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((user_info.address, user_info.port))
    user = User(info=user_info, socket=s)
    
    app = configure_app(user)
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

    run_event = threading.Event()
    run_event.set()
    read_queue = Queue()
    t = ComThread(user=user, run_event=run_event, read_queue=read_queue)
    t.start()

    # t2 = ClientTerminalDashboard(
    #     user=user, run_event=run_event, queue=read_queue
    # )
    # t2.start()

    try:
        t.join()
        # t2.join()
    except KeyboardInterrupt:
        run_event.clear()
        t.join()
        # t2.join()
