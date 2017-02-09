#!/usr/bin/env python

import curses,serial,time

if __name__ == "__main__":
    # setup serial
    ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.05)
    
    # wait a bit
    time.sleep(0.5)

    a=chr(30)+chr(0x0)+'abcdefghijklmnopqrstuvwxyz\nabc'
    ser.write(a)
    time.sleep(2)
    r = ser.read(100)
    print(r)
    ser.close()
