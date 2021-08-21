#!/usr/bin/env python3

import os
import socket
import threading 
import time
import sys
import argparse

c_list_lock = threading.Lock()
log_lock = threading.Lock()
connection_list = []
connection_number = 0
active_connection = 0
server_running = False

log_buffer = []

def setup_argument_parser():
    parser = argparse.ArgumentParser(prog='Server-side connection manager',\
                                     usage='python3 Connection_manager_server.py -a <IP address> -p <Port>',\
                                     description='Program designed to keep track of the availability of a remote machine')

    # metavar='' so that there is no all caps argument name in usage
    parser.add_argument('-a', '--address', default='localhost', metavar='', help='the machine\'s IP address')
    parser.add_argument('-p', '--port', type=int, default=65432, metavar='', help='port used for the connection')
    
    return parser

def get_arguments(parser):
    args = parser.parse_args()
    return args.address, args.port

def log_write_info(string):
    global log_buffer
    log_line = "[ INFO ] : " + string
    log_lock.acquire()
    log_buffer.append(log_line)
    log_lock.release()

def log_write_warning(string):
    global log_buffer
    log_line = "[\033[38;5;214mWARNING\033[0m]: " + string
    log_lock.acquire()  
    log_buffer.append(log_line)
    log_lock.release()  

def log_write_error(string):
    global log_buffer
    log_line = "[ \033[38;5;160mERROR\033[0m ]: " + string
    log_lock.acquire()
    log_buffer.append(log_line)
    log_lock.release()



def client_handler(client, addr):
    global connection_list
    global connection_number
    global active_connection

    client_data = [connection_number, *addr, "DUMMY NAME"]
    log_write_info("new client accepted : {}".format(client_data))

    c_list_lock.acquire()
    connection_list.append(client_data)
    connection_number += 1
    active_connection += 1
    c_list_lock.release()

    while True:
        data = client.recv(1024)
        if not data:
            break
        elif data == b"END_CONNECTION":
            client.sendall(b"Connection ended per client request")
            break
        log_write_info("Client #{} sent : {}".format(client_data[0], data))
        client.sendall(data)
        log_write_info("Echo sent back")
    client.close()

    c_list_lock.acquire()
    connection_list.remove(client_data)
    active_connection -= 1
    c_list_lock.release()
    log_write_info("Client #{} disconnected".format(client_data[0]))

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def print_log_buffer(offset, max_len):
    global log_buffer
    log_lock.acquire()
    local_log_buffer = log_buffer.copy()
    log_lock.release()
    try:
        print("\033[2;0H\033[?25l", end="\r")
        nb_lines = os.get_terminal_size().lines - 5
        start_val = max(len(local_log_buffer) - nb_lines, 0)
        for line in local_log_buffer[start_val:]:
            print("\033[{offset}C\u2016\t{text}".format(offset=offset, text=line[:max_len]))
        print("\033[?25h",end="\r")
    except KeyboardInterrupt:
        print("\033[?25h",end="\r")

def server_log():
    global connection_list
    global active_connection
    local_connection_list = []
    print_flag = False 

    global log_buffer
    local_log_buffer = []
    log_print_flag = False

    cls()

    size = os.get_terminal_size()

    header = ["Connection list:", "Server logs: "]
    columns = ["ID", "ADDR", "PORT", "NAME"]
    separations = []
    for i in columns:
        separations.append("")

    header_format = "\033[1;38;5;118m{:^{w}}\033[0m" * len(header)
    row_format = "|{:{fill}^6}|{:{fill}^12}|{:{fill}^10}|{:{fill}^20}|"

    print(header_format.format("Connection list:", "Server logs: " ,w=size.columns//2))
    print(row_format.format(*separations, fill="\u203e"))
    print(row_format.format(*columns, fill=""))
    print(row_format.format(*separations, fill="_"))

    while server_running == True:

        c_list_lock.acquire()
        if local_connection_list != connection_list:
            local_connection_list = connection_list.copy()
            print_flag = True
        c_list_lock.release()

        if print_flag == True:
            log_write_info("Updating connecting list display")
            print("\033[4;0H\033[J", end="\r")
            for item in local_connection_list:
                print(row_format.format(*separations, fill="-"))
                print(row_format.format( *item,fill=""))
            print(row_format.format(*separations, fill="_"))
            print_flag = False
        
        log_lock.acquire()
        if local_log_buffer != log_buffer:
            local_log_buffer = log_buffer.copy()
            log_print_flag = True
        log_lock.release()

        if log_print_flag == True:
            print_log_buffer(size.columns//2, size.columns//2)
            log_print_flag = False
        time.sleep(0.1)
    

def launchServer(host, port):
    global server_running
    c_list_lock.acquire()
    server_running = True
    c_list_lock.release()

    log_thread = threading.Thread(target=server_log)
    log_thread.start()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bound = False
    while not bound:
        try:
            s.bind((host, port))
            bound = True
            log_write_info("bind successfull")
        except OSError:
            log_write_error("Failed to bind, trying again in 5 seconds...")
            time.sleep(5)
    s.listen(2)
    i = 0
    while True:
        try:
            conn, addr = s.accept()
        except KeyboardInterrupt:
            c_list_lock.acquire()
            server_running = False
            c_list_lock.release()
            break
        #print('Connected by', addr)
        t = threading.Thread(target=client_handler, args=(conn, addr))
        t.start()

    t.join()
    s.close()

def main(argv):
    parser = setup_argument_parser()
    host, port = get_arguments(parser)

    log_write_info("launching connection manager")    
    launchServer(host, port)
    log_write_info ("server exit")
    

if __name__ == "__main__":
    main(sys.argv[1:])