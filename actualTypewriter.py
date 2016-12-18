#!/usr/bin/env python

import curses,serial,time

if __name__ == "__main__":
    # setup serial
    ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.5)
    
    # wait a bit
    time.sleep(0.5)

    screen = curses.initscr()
    try:
        curses.noecho()
        # curses.curs_set(0) # to hide cursor
        screen.keypad(1)
        screen.addstr("Please start typing! (ctrl-c or ctrl-d to quit)\n")
        while True:
            event = screen.getch()
            if event == curses.KEY_UP:
                event = 0 # special char for typewriter
            elif event == curses.KEY_DOWN:
                event = 1
            elif event == curses.KEY_LEFT:
                event = 2
            elif event == curses.KEY_RIGHT:
                event = 3
            elif event == curses.KEY_BACKSPACE:
                event = 0x7f
            #elif event == 0x7f: # already backspace
            #    pass
            else:
                screen.addch(event)
            ser.write(chr(event))
            time.sleep(0.1)
    finally:
        curses.endwin()
        ser.close()
