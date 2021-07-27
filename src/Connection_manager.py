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
    # for clients
        -a, --addr: remote machine's IP address
        -p, --port: port used for the connection
        -c, --cmd : command used for the connection
    # for server
        --server : Run as server
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

def launchClient(host, port, cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

    print('Received', repr(data))
    if cmd != '':
        print("Launching cmd : {}".format(cmd))
        os.system(cmd)

def main(argv):
    
    host = 'localhost'
    port = 65432
    cmd = ''
    print("launching connection manager")
    try:
        opts, args = getopt.getopt(argv, "a:p:c:h", ["addr=","port=","cmd=","server", "help"])
      
    except getopt.GetoptError as e:
        print("Error : {}".format(e.msg))
        usage()
        sys.exit(2)
  
    for opt, arg in opts:
        if opt in ['-a', 'addr']:
            host = arg
        elif opt in ['-p', 'port']:
            port = arg
        elif opt in ['-c', 'cmd']:
            cmd = arg
        elif opt in ['-h', 'help']:
            usage()
            sys.exit(0)
            

    if "--server" in argv :
        launchServer(host, port, cmd)
        print ("server exit")
    else:
        launchClient(host, port, cmd)
        print ("client exit")

if __name__ == "__main__":
    main(sys.argv[1:])