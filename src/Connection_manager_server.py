#!/usr/bin/env python

import os
import socket
import sys
import getopt

def usage():
    print("--------------Connection_manager--------------")

    print("""Brief: Program designed to keep track of
availability of a remote machine""")
    print("""python3 Connection_manager.py -a <IP address> -p <Port> -c <"Command">""")
    print("""Parameters:
        -a, --addr: machine's IP address
        -p, --port: port used for the connection""")

def launchServer(host, port, cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    print('Connected by', addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)

def main(argv):
    
    host = 'localhost'
    port = 65432
    cmd = ''
    print("launching connection manager")
    try:
        opts, args = getopt.getopt(argv, "a:p:h", ["addr=","port=","server", "help"])
      
    except getopt.GetoptError as e:
        print("Error : {}".format(e.msg))
        usage()
        sys.exit(2)
  
    for opt, arg in opts:
        if opt in ['-a', 'addr']:
            host = arg
        elif opt in ['-p', 'port']:
            port = arg
        elif opt in ['-h', 'help']:
            usage()
            sys.exit(0)
    
    launchServer(host, port, cmd)
    print ("server exit")

if __name__ == "__main__":
    main(sys.argv[1:])