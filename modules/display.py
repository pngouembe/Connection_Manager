#!/usr/bin/env python3

import threading
import os
import time

def cls():
    os.system('cls' if os.name=='nt' else 'clear')


class WebLogger(threading.Thread):
    def __init__(self) -> None:
        self.log_buffer = []
        self.lock = threading.Lock()
        threading.Thread.__init__(self)

    err_level = 0
    warn_level = 1
    info_level = 2
    dbg_level = 3

    def log(self, level, msg) -> None:
        self.lock.acquire()
        self.log_buffer.append([level, msg])
        self.lock.release()


class Logger(threading.Thread):
    #
    def __init__(self, title='', x=0, y=0, row=0, col=0) -> None:
        """
        Parameters
        ----------
        x : int, default=0, x offset on screen
        y : int, default=0, y offset on screen
        row : int, default=0, number of rows printed on screen
        col : int, default=0, number of columns printed on screen

        """
        self.title = title
        self.x_off = x
        self.y_off = y
        self.size = os.get_terminal_size()
        # remove top and bottom lines from number of
        # printable rows
        # lines used for the title are also removed
        self.row_off = 2 if self.title == '' else 4
        if row == 0:
            # not counting first and last line
            self._rows = self.size.lines - self.row_off - y
        else:
            self._rows = min(row - self.row_off, self.size.lines - y - self.row_off - 1)

        if col == 0:
            self._cols = self.size.columns - max(x,1)
        else:
            self._cols = min(col, self.size.columns - x)

        # not counting last caracter of the line
        self.line_len = self._cols - 1
        self.endl = self.x_off + self._cols
        self.log_buffer = []
        self.lock = threading.Lock()
        self.sem = threading.Semaphore()
        self.Logger_enabled = True
        threading.Thread.__init__(self)

    err_level = "[ \033[38;5;160mERROR\033[0m ]:"
    warn_level = "[\033[38;5;214mWARNING\033[0m]:"
    info_level = "[ INFO  ]:"
    dbg_level = "[ DEBUG ]:"

    def log(self, level, msg) -> None:
        self.lock.acquire()
        self.log_buffer.append([level, msg])
        self.lock.release()
        self.sem.release()

    def print_buffer(self) -> None:
        print("\033[{v_off};0H".format(v_off=self.y_off), end="\r")
        print("\033[{h_off}G".format(h_off=self.x_off), end="")
        print("\u2554{:\u2550^{w}}\u2557".format("", w=self.line_len))
        if self.title != '':
            print("\033[{h_off}G".format(h_off=self.x_off), end="")
            print("\u2551\033[1;38;5;118m{:^{w}}\033[0m\u2551".format(self.title, w=self.line_len))
            print("\033[{h_off}G".format(h_off=self.x_off), end="")
            print("\u2560{:\u2550^{w}}\u2563".format("", w=self.line_len, h_off=self.x_off))
            #self._rows = self._rows - 2

        i = 0
        for line in self.log_buffer[max(len(self.log_buffer)-self._rows, 0):]:
            tmp = ' '.join(line)
            print("\033[{h_off}G".format(h_off=self.x_off), end="")
            print("\u2551{:<{w}}".format(tmp, w=self.line_len))
            i += 1

        while i < self._rows :
            print("\033[{h_off}G".format(h_off=self.x_off), end="")
            print("\u2551{:^{w}}\u2551".format("", w=self.line_len))
            i += 1

        print("\033[{h_off}G".format(h_off=self.x_off), end="")
        print("\u255A{:\u2550^{w}}\u255D".format("", w=self.line_len),end="")

    def kill(self) ->None:
        self.Logger_enabled = False
        self.sem.release()

    def run(self) -> None:
        while self.Logger_enabled:
            self.print_buffer()
            self.sem.acquire()



class LoggerMgr():
    Loggers=[]
    # The init function should take a config file or a dictionary
    # containing loggers informations
    def __init__(self,logger_list=None,logger_cfg_file=None) -> None:
        # Need to init all the Loggers objects wanted by user
        if logger_list == None and logger_cfg_file == None:
            self.Loggers.append(Logger("test"))

    def launch_logger_mgr(self) -> None:
        # Hiding cursor
        print("\033[?25l",end="")
        # Starting all the logger threads
        for item in self.Loggers:
            item.start()
            # item.log(item.err_level, "test du log server")

        # Waiting for all loggers to finish
        # for item in self.Loggers:
        #     item.join()

    def stop_logger_mgr(self) -> None:
        # Making cursos visible
        print("\033[?25h",end="")
        for item in self.Loggers:
            item.kill()

if __name__ == "__main__":
    from random import randint
    log_mgr = LoggerMgr()
    Log : Logger = log_mgr.Loggers[0]
    log_mgr.launch_logger_mgr()
    for i in range(250):
        slp_time_ms = randint(0,50) / 1000
        time.sleep(slp_time_ms)
        Log.log(Log.info_level, "{} : Slept for {} milliseconds".format(i, slp_time_ms))
    log_mgr.stop_logger_mgr()
