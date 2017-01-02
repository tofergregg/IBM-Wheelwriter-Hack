#!/usr/bin/env python
import serial
import time
import sys
import math
import os

MAXLINE = 60 

if len(sys.argv) != 2:
    print("Usage:\n\ttextToBean filename")
    quit()

filePath = sys.argv[1]

ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.1)
# wait a bit
time.sleep(0.5)

# get the file length
fileLen = os.path.getsize(filePath)

# first two bytes are the file length (max: 65K)
# sent in little-endian format
stringHeader = chr(0x00) + chr(fileLen & 0xff) + chr(fileLen >> 8)
try:
    with open(filePath,"r") as f:
        # read MAXLINE characters at a time and send
        while True: 
            chars = f.read(MAXLINE)
            if (chars == ''):
                break
            ser.write(stringHeader + chars)
            stringHeader = '' # not needed any more
            sys.stdout.write(chars)
            sys.stdout.flush()
            response = ""
            while True:
                response += ser.read(10)
                if len(response) > 0 and response[-1] == '\n':
                    #print("(bytes written:"+response.rstrip()+")")
                    break
                time.sleep(0.1)
except KeyboardInterrupt:
    pass
ser.close()
