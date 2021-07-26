#!/usr/bin/env python

import os
import socket
import sys

HOST = 'localhost'
PORT = 65432

def launchServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    print('Connected by', addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)

def launchClient():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

    print('Received', repr(data))

def main(argv):
    print("launching connection manager")
    if "--server" in argv :
        launchServer()
    else:
        launchClient()

if __name__ == "__main__":
    main(sys.argv[1:])