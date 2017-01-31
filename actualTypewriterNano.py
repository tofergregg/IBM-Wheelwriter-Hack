#!/usr/bin/env python
# coding=utf-8

# note: if you are on linux, you might have to run
# with sudo
# If you don't want to run with sudo, you can try
# adding dialout to your user (requires a logout to
# take effect:
#    $ sudo usermod -a -G dialout $USER

# note 2: if you are on Windows, you will have to
# install both pyserial and curses
# To install pyserial:
#   pip install pyserial
# To install curses:
# Go to http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
# and download the curses program (possibly win32)
# In a command window, type:
#   pip install pathToFileYouDownloaded
# e.g., pip install \Users\Tofer\Downloads\curses‑2.2‑cp27‑none‑win32.whl 

import curses
import serial
import time
import availablePorts
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        portChoiceInt = int(sys.argv[1])
    else:
        portChoiceInt = 0
    # choose port
    ports = availablePorts.serial_ports()

    if len(ports) == 1:
        # just choose the first
        portChoice = ports[0]
    else:
        if portChoiceInt == 0:
            print("Please choose a port:")
            for idx,p in enumerate(ports):
                print("\t"+str(idx+1)+") "+p)
            portChoiceInt = int(input())
        portChoice = ports[portChoiceInt-1]
    # setup serial
    ser = serial.Serial()
    ser.port = portChoice
    ser.baudrate = 115200
    ser.timeout = 0.1
    ser.setDTR(False)
    ser.open()
    #ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.1)

    # wait a bit
    time.sleep(2)

    screen = curses.initscr()
    try:
        curses.noecho()
        # curses.curs_set(0) # to hide cursor
        screen.keypad(1)
        screen.addstr("Please start typing! (ctrl-c or ctrl-d to quit)\n")
        while True:
            event = screen.getch()
            if event == curses.KEY_UP:
                event = 128  # special char for typewriter
            elif event == curses.KEY_DOWN:
                event = 129
            elif event == curses.KEY_LEFT:
                event = 130
            elif event == curses.KEY_RIGHT:
                event = 32  # space
            elif event == curses.KEY_BACKSPACE:
                event = 0x7f
            elif event == 0x7f:  # already backspace
                pass
            elif event == 393:  # shift left-arrow for micro-backspace
                event = 131
            elif event == 21:
                screen.addstr('(underline)')
                event = 3 # convert to code for underline
            elif event == 2:
                screen.addstr('(bold)')
            else:
                screen.addch(event)
            # screen.addstr(str(type(event)))
            ser.write(chr(event))  # send one byte
            ser.flush()
            response = ''
            while True:
                response = ser.read(10)
                # print(response)
                if len(response) > 0 and 'ok' in response:
                    # print("(bytes written:"+response.rstrip()+")")
                    break
                time.sleep(0.01)
    finally:
        curses.endwin()
        ser.close()
