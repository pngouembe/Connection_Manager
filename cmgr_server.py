#!/usr/bin/env python3
from config.server import ServerConfig as config
from rich import print, inspect
from rich.pretty import pprint
from server import launch_server
from sdataclasses.servers import Server

def main():
    cfg_dict = config.as_dict()
    server = Server(**cfg_dict)
    inspect(server)
    launch_server(server_config=server)

if __name__ == "__main__":
    main()
