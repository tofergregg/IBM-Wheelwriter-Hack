#!/usr/bin/env python

import curses,serial,time

if __name__ == "__main__":
    # setup serial
    ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.05)
    
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
            elif event == 0x7f: # already backspace
                pass
            elif event == 393: # shift left-arrow for micro-backspace
                event = 6 # what the Arduino is expecting
            else:
                screen.addch(event)
            #screen.addstr(str(event))
            ser.write(chr(event))
            while True:
                written = ser.read(5) # no more than 5 characters
                if len(written) > 0:
                    break
            #time.sleep(0.25)
    finally:
        curses.endwin()
        ser.close()
