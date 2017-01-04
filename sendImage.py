#!/usr/bin/env python

from PIL import Image
import sys
import time
import sys
import math
import os
import serial

MAXLINE = 60

if len(sys.argv) != 2:
    print("Usage:\n\t./sendImage image")
    quit()
im = Image.open(sys.argv[1])
im = im.convert('RGB')

b = im.tobytes()

b2 = ''
for idx,byte in enumerate(b):
    if ord(byte) < 150:
        b2 += chr(0)
    else:
        b2 += chr(255)

im2 = Image.frombytes('RGB',(im.width,im.height),b2)
im2.show()

bits = []
for r in range(0,im2.height*3,3):
    for c in range(0,im2.width*3,3):
        #print(ord(b2[r * im2.width + c]))
        #print(r,c)
        if (ord(b2[r * im2.width + c]) == 0):
            sys.stdout.write('.')
            bits.append(chr(1));
        else:
            sys.stdout.write(' ')
            bits.append(chr(0))
    sys.stdout.write('\n')

ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.1)
# wait a bit
time.sleep(0.5)

stringHeader = chr(0x01) + chr(im2.width) + chr(im2.height)

try:
    ser.write(stringHeader)

    # send MAXLINE characters at a time 
    while len(bits) > 0: 
        chunk = bits[:MAXLINE]
        bits = bits[MAXLINE:]
        if (chunk == ''):
            break
        ser.write(chunk)
        print("Sent "+str(len(chunk))+" bits")
        response = ""
        while True:
            response += ser.read(10)
            print(response)
            if len(response) > 0 and response[-1] == '\n':
                #print("(bytes written:"+response.rstrip()+")")
                break
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
ser.close()

