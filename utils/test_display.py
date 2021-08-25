#!/usr/bin/env python3

import os
import time
import sys
sys.path.append('../modules')
from display import Logger, LoggerMgr


log_buffer = []

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

cls()

def log_write_info(string):
    global log_buffer
    log_line = "[ INFO ] : " + string
    log_buffer.append(log_line)

def log_write_warning(string):
    global log_buffer
    log_line = "[\033[38;5;214mWARNING\033[0m]: " + string
    log_buffer.append(log_line)

def log_write_error(string):
    global log_buffer
    log_line = "[ \033[38;5;160mERROR\033[0m ]: " + string
    log_buffer.append(log_line)


    

def print_log_buffer(offset, max_len):
    global log_buffer
    print("\033[2;0H\033[?25l", end="\r")
    nb_lines = os.get_terminal_size().lines - 5
    start_val = max(len(log_buffer) - nb_lines, 0)
    for line in log_buffer[start_val:]:
        print("\033[{offset}C\u2016\t{text}".format(offset=offset, text=line[:max_len]))
    print("\033[?25h",end="\r")

size = os.get_terminal_size()

header = ["Connection list:", "Server logs: "]
columns = ["ID", "ADDR", "PORT", "NAME"]
rows = [[0, "127.0.0.1", 654321, "DUMMY NAME JOE"], [1, "127.0.0.1", 654321, "DUMMY NAME JOHN"]]
logs = []
separations = []
for i in columns:
    separations.append("")

header_format = "\033[1;38;5;118m{:^{w}}\033[0m" * len(header)
row_format = "|{:{fill}^6}|{:{fill}^12}|{:{fill}^10}|{:{fill}^20}|"

print(header_format.format("Connection list:", "Server logs: " ,w=size.columns//2))
print(row_format.format(*separations, fill="\u203e"))
print(row_format.format(*columns, fill=""))
for item in rows:
    print(row_format.format(*separations, fill="-"))
    print(row_format.format( *item,fill=""))
print(row_format.format(*separations, fill="_"))
i=0
while i < 10:
    if i%3 == 1:
        log_write_warning("numero : {}".format(i))
    elif i%3 == 2:
        log_write_error("numero : {}".format(i))
    else:
        log_write_info("numero : {}".format(i))

    print_log_buffer(size.columns//2, size.columns//3)
    i+=1
    time.sleep(0.1)

size=os.get_terminal_size()
Log1 = Logger("Test logger", size.columns//2, 15,7)

i=0
Log1.print_buffer()
while i < 10:
    time.sleep(0.1)
    if i%3 == 1:
        Log1.log(Log1.warn_level, "numero : {}".format(i))
    elif i%3 == 2:
        Log1.log(Log1.err_level, "numero : {}".format(i))
    else:
        Log1.log(Log1.info_level, "numero : {}".format(i))

    Log1.print_buffer()
    i+=1


Log_mgr = LoggerMgr()
Log_mgr.launch_logger_mgr()
Log2 = Log_mgr.Loggers[0]
for i in range(10):
    time.sleep(0.1)
    Log2.log(Log2.err_level, "test du log user # {}".format(i))

Log_mgr.stop_logger_mgr()