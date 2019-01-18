#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys

def setAddress(ADDR,n):
    '''Sets each pin in ADDR to its corresponding bit from n'''
    for i,p in enumerate(ADDR):
        GPIO.output(p, n & (1 << i))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:\n\t{} output.bin".format(sys.argv[0]))
        quit()

    GPIO.setmode(GPIO.BCM)

    # datasheet: https://www.datasheets360.com/pdf/1277907997291200345?xrefPartId=1277907997291200345&alternatePartManufacturerId=0
    # KM23C256 pins 

    #ADDR = [1,7,8,25,24,23,18,15,4,17,10,27,14,3,2]
    ADDR = [1,7,8,25,24,23,18,15,4,17,10,27,14,3,2,26,19]
    DATA = [12,16,20,13,6,5,0,11]
    CE = 9
    OE = 22

    # set address pins as output
    for p in ADDR:
        GPIO.setup(p, GPIO.OUT)

    # set CE and OE as output
    GPIO.setup(CE, GPIO.OUT)
    GPIO.setup(OE, GPIO.OUT)

    # set data pins as input
    for p in DATA:
        GPIO.setup(p, GPIO.IN)

    # read all 32K bytes of data 
    all_data = []
    #for a in range(32768):
    for a in range(32768*4):
        setAddress(ADDR,a)

        # read data
        d = 0
        for i,p in enumerate(DATA):
            d = d | (GPIO.input(p) << i)

        print(hex(d))
        all_data.append(d)

    GPIO.cleanup()

    # print data to file
    all_data = bytes(all_data)
    with open(sys.argv[1],"wb") as f:
        f.write(all_data)
