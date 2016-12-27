#!/usr/bin/env python
import serial
import time
import sys
import math

MAXLINE = 30

if len(sys.argv) != 2:
    print("Usage:\n\ttextToBean filename")
    quit()

ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.1)
# wait a bit
time.sleep(0.5)
with open(sys.argv[1],"r") as f:
    for line in f:
        line = line[:-1] # remove newline
        partialLine = line 
        # only send up to MAXLINE characters at a time
        for chunk in range(int(math.ceil(len(partialLine) / float(MAXLINE)))):
            partialLine = line[:MAXLINE]
            line = line[MAXLINE:]
            while len(partialLine) != 0:
                written = ser.write(partialLine)
                sys.stdout.write(partialLine+"(bytes sent:"+str(written)+")")
                sys.stdout.flush()
                partialLine = partialLine[written:]
                # wait fora response with the number of characters printed
                response = ""
                while True:
                    response += ser.read() # read next byte 
                    if len(response) > 0 and response[-1] == '\n':
                        print("(bytes written:"+response.rstrip()+")") # don't print newline
                        break
                    time.sleep(0.2) # wait a bit before checking again
        # send the return
        written = ser.write('\n')
        sys.stdout.write("(sent return)")
        sys.stdout.flush()
        response = ""
        while True:
            response += ser.read(10)
            if len(response) > 0 and response[-1] == '\n':
                print("(bytes written:"+response.rstrip()+")")
                break
            time.sleep(0.2)

ser.close()
