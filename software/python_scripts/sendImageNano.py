#!/usr/bin/env python2.7
# coding=utf-8

# note: if you are on linux, you might have to run
# with sudo
# If you don't want to run with sudo, you can try
# adding dialout to your user (requires a logout to
# take effect:
#    $ sudo usermod -a -G dialout $USER

import sys
import time

import serial
from PIL import Image
import availablePorts

MAXWIDTH = 500

# if HARDCODED_PORT is '' then the user will be given a choice
#HARDCODED_PORT = '/dev/tty.wchusbserial1410'
HARDCODED_PORT = ''

if len(sys.argv) != 2:
    print("Usage:\n\t./sendImage image [port choice]")
    quit()
im = Image.open(sys.argv[1])
im = im.convert('RGB')

if len(sys.argv) > 2:
    portChoiceInt = int(sys.argv[2])
else:
    portChoiceInt = 0
# choose port
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

# resize to at most MAXWIDTH  wide
if im.width > MAXWIDTH:
    wpercent = (MAXWIDTH / float(im.width))
    hsize = int((float(im.height) * float(wpercent)))
    im = im.resize((MAXWIDTH, hsize), Image.ANTIALIAS)
b = im.tobytes()

b2 = ''
for idx, byte in enumerate(b):
    if ord(byte) < 150:
        b2 += chr(0)
    else:
        b2 += chr(255)

im2 = Image.frombytes('RGB', (im.width, im.height), b2)
im2.show()

# convert to run-length encoded stream
# Format for bytes: (number of bits low byte)(number of bits high byte)(char to print)
# char to print will normally be a period (.) or a space ( ) but will eventually
# include an underscore (_) for faster printing

runs = [(1, 0, 0)]
for r in range(0, im2.height * 3, 3):
    prevBit = ord(b2[r * im2.width])
    bitCount = 0
    lineBits = 0
    for c in range(0, im2.width * 3, 3):
        currentBit = ord(b2[r * im2.width + c])
        if currentBit != prevBit:
            # sys.stdout.write(str(bitCount))
            if prevBit == 0:
                # sys.stdout.write('.')
                runs.append((bitCount & 0xff, bitCount >> 8, ord('.')))
            else:
                # sys.stdout.write('x')
                runs.append((bitCount & 0xff, bitCount >> 8, ord(' ')))
            lineBits += bitCount
            bitCount = 0
            prevBit = currentBit
        bitCount += 1
        # print(ord(b2[r * im2.width + c]))
        # print(r,c)
        # if ord(b2[r * im2.width + c]) == 0:
        #    sys.stdout.write('.')
        #    bits.append(chr(1));
        # else:
        #    sys.stdout.write(' ')
        #    bits.append(chr(0))
    if prevBit == 0:  # 0 means black
        # don't bother printing a string of spaces at the end, just 1s
        # sys.stdout.write(str(bitCount)+'.')
        runs.append((bitCount & 0xff, bitCount >> 8, ord('.')))
        lineBits += bitCount
    # sys.stdout.write('\n')
    runs.append((lineBits & 0xff, lineBits >> 8, ord('\n')))

runs.append((0, 0, 0))  # signal to end the image printing
#print runs
#quit()

ser = serial.Serial(portChoice, 115200, timeout=0.1)
# wait a bit
time.sleep(2)

stringHeader = chr(0x01)

try:
    ser.write(stringHeader)

    while len(runs) > 0:
        run = runs[:20] # send up to 60 bytes at a time
        runs = runs[20:]
        sendStr = ''
        for r in run:
            sendStr += ''.join([chr(x) for x in r])
        ser.write(sendStr)
        print("Sent " + str(run))
        response = ""
        while True:
            response += ser.read(10)
            print(response)
            if len(response) > 0 and '\n' in response:
                # print("(bytes written:"+response.rstrip()+")")
                break
            time.sleep(0.01)
        if "timeout" in response or "done" in response:
            print(response)
            break
    print("Done.")
except KeyboardInterrupt:
    pass
ser.close()
