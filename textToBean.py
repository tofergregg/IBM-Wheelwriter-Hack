#!/usr/bin/env python
import serial
import time
import sys

if len(sys.argv) != 2:
    print("Usage:\n\ttextToBean filename")
    quit()

ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.5)
# wait a bit
time.sleep(0.5)
with open(sys.argv[1],"r") as f:
    for line in f:
        print(len(line))
        while len(line) != 0:
            written = ser.write(line)
            line = line[written:]
            time.sleep(0.1 * written) # wait 1/10 of a second per character sent
#        bytesAvail = ser.in_waiting
#        if bytesAvail > 0:
#            rec = ser.read(bytesAvail)
#            if len(rec) > 0:
#                print(rec)
ser.close()
