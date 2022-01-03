#!/usr/bin/env python3
from config.server import ServerConfig as config
from rich import print, inspect
from rich.pretty import pprint
from server import launch_server
from server.dataclass import server_from_dict

def main():
    cfg_dict = config.as_dict()
    pprint(cfg_dict, expand_all=True)
    server = server_from_dict(cfg_dict)
    launch_server(server_config=server)

if __name__ == "__main__":
    main()
