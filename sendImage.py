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

# convert to run-length encoded stream
# Format for bytes: (number of bits low byte)(number of bits high byte)(char to print)
# char to print will normally be a period (.) or a space ( ) but will eventually
# include an underscore (_) for faster printing

runs = [(1,0,0)]
for r in range(0,im2.height*3,3):
    prevBit = ord(b2[r * im2.width])
    bitCount = 0
    for c in range(0,im2.width*3,3):
        currentBit = ord(b2[r * im2.width + c])
        if currentBit != prevBit:
            #sys.stdout.write(str(bitCount))
            if prevBit == 0:
                #sys.stdout.write('.')
                runs.append((bitCount & 0xff, bitCount >> 8, '.'))
            else:
                #sys.stdout.write('x')
                runs.append((bitCount & 0xff, bitCount >> 8,' '))
            bitCount = 0
            prevBit = currentBit
        bitCount+=1
        #print(ord(b2[r * im2.width + c]))
        #print(r,c)
        #if ord(b2[r * im2.width + c]) == 0:
        #    sys.stdout.write('.')
        #    bits.append(chr(1));
        #else:
        #    sys.stdout.write(' ')
        #    bits.append(chr(0))
    if prevBit == 0: # 0 means black
        # don't bother printing a string of spaces at the end, just 1s
        #sys.stdout.write(str(bitCount)+'.')
        runs.append((bitCount & 0xff, bitCount >> 8,'.'))
    #sys.stdout.write('\n')
    runs.append((1,0,'\n'))

runs.append((0,0,0)) # signal to end the image printing
#print runs

ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.1)
# wait a bit
time.sleep(0.5)

stringHeader = chr(0x01)

try:
    ser.write(stringHeader)

    # send MAXLINE characters at a time 
    while len(bits) > 0: 
        run = bits[0]
        bits = bits[1:]
        ser.write(''.join([chr(x) for x in run]))
        print("Sent "+str(run))
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

