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

# if HARDCODED_PORT is '', then the user will get a choice
#HARDCODED_PORT = '/dev/tty.wchusbserial1410'
HARDCODED_PORT = ''

if len(sys.argv) > 1:
    portChoice = sys.argv[1]
else:
    portChoice = None
    portChoiceInt = 0
# choose port
if portChoice == None:
    if HARDCODED_PORT == '':
        ports = availablePorts.serial_ports()

        if len(ports) == 1:
            # just choose the first
            print("Choosing: " + ports[0])
            portChoice = ports[0]
        else:
            if portChoiceInt == 0:
                print("Please choose a port:")
                for idx,p in enumerate(ports):
                    print("\t"+str(idx+1)+") "+p)
                portChoiceInt = int(input())
            portChoice = ports[portChoiceInt-1]
    else: 
        portChoice = HARDCODED_PORT

# set up serial port
ser = serial.Serial(portChoice, 115200, timeout=0.1)
# wait a bit
time.sleep(2)

# The horizontal and vertical microspaces are capped at +-32767
# If either value is negative, we will convert it to two's complement
# which will be easy to read on the Arduino
#
# We will convert each value to a 2-byte value in little endian 
# format to transfer

bytesToSend = chr(0x04) 

try:
        ser.write(bytesToSend)
        response = ""
        while True:
            response += ser.read(10)
            #print("resp:"+response)
            if len(response) > 0 and response[-1] == '\n':
                print("response:"+response)
                break
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
ser.close()
