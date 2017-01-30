#!/usr/bin/env python
# coding=utf-8

# note: if you are on linux, you might have to run
# with sudo
# If you don't want to run with sudo, you can try
# adding dialout to your user (requires a logout to
# take effect:
#    $ sudo usermod -a -G dialout $USER

import os
import sys
import time
import availablePorts
import serial

MAXLINE = 60

if len(sys.argv) == 1:
    print("Usage:\n\ttextToBean filename")
    quit()

filePath = sys.argv[1]
if len(sys.argv) > 2:
    portChoiceInt = int(sys.argv[2])
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
ser = serial.Serial(portChoice, 115200, timeout=0.1)
# wait a bit
time.sleep(2)

# get the file length
fileLen = os.path.getsize(filePath)

# first two bytes are the file length (max: 65K)
# sent in little-endian format
stringHeader = chr(0x00) + chr(fileLen & 0xff) + chr(fileLen >> 8)
try:
    with open(filePath, "r") as f:
        # read MAXLINE characters at a time and send
        while True:
            chars = f.read(MAXLINE)
            if chars == '':
                break
            ser.write(stringHeader + chars)
            stringHeader = ''  # not needed any more
            sys.stdout.write(chars)
            sys.stdout.flush()
            response = ""
            while True:
                response += ser.read(10)
                #print("resp:"+response)
                if len(response) > 0 and response[-1] == '\n':
                    # print("(bytes written:"+response.rstrip()+")")
                    break
                time.sleep(0.1)
except KeyboardInterrupt:
    pass
ser.close()
