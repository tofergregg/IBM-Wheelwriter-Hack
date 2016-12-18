#!/usr/bin/env python
import serial
import time
import sys
import math

if len(sys.argv) != 2:
    print("Usage:\n\ttextToBean filename")
    quit()

ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.5)
# wait a bit
time.sleep(0.5)
with open(sys.argv[1],"r") as f:
    for line in f:
        partialLine = line
        # only send up to 50 characters at a time
        for chunk in range(int(math.ceil(len(line) / 50.0))):
            partialLine = line[:50]
            line = line[50:]
            while len(partialLine) != 0:
                written = ser.write(partialLine)
                sys.stdout.write(partialLine+"(bytes sent:"+str(written)+")")
                sys.stdout.flush()
                partialLine = partialLine[written:]
                # wait fora response with the number of characters printed
                while True:
                    response = ser.read(10) # read up to 10 bytes
                    if len(response) > 0:
                        print("(bytes written:"+response[:-2]+")") # don't print newline
                        break
                    time.sleep(0.2) # wait a bit before checking again
ser.close()
