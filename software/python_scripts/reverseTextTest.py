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

def parseMarkdown(text):
    '''We are looking for __underline__ and **bold**
       text. Nothing fancy, and we are expecting that
       the markdown will be perfect (e.g., missing tags
       are not handled particularly gracefully)
       The basic idea: __ toggles underline and
       ** toggles bold. Either can be escaped with
       a leading backslash ('\').

       We are also going to parse the text for newlines, and
       reverse the text at each newline. Newlines just become: 
    '''
    BOLD_CODE = chr(2) # will be sent to arduino to toggle bold
    UNDERLINE_CODE = chr(3) # sent to arduino to toggle underline
    parsedText = ''
    escaped = False
    skipnext = False
    for idx,c in enumerate(text):
        if skipnext: 
            skipnext = False
            continue
        if escaped:
            parsedText += c
            escaped = False
        elif c == '\\': # look for escape character
            escaped = True
        elif c == '*':
            # lookahead one char
            if idx < len(text) - 1 and text[idx+1] == '*':
                parsedText+=BOLD_CODE
                skipnext = True
            else:
                parsedText+=c
        elif c == '_':
            # lookahead one char
            if idx < len(text) - 1 and text[idx+1] == '_':
                parsedText+=UNDERLINE_CODE
                skipnext = True
            else:
                parsedText+=c
        else:
            parsedText += c
    return parsedText

def placeReverses(text):
    """This function places reverse markers
       into the text, based on line breaks.
       The algorithm will find a return,
       then determine if the print head
       is closer to the left or the end
       of the next line of text.
       It will then output REVERSE_CODE,
       then a 0 to indicate we will be printing
       in the forwards direction, 1 for reverse printing.
       Then one byte for the number of spaces to go
       forward or backwards after the newline, 
       and another 0 for backwards spaces, or 1
       for forward spaces
    """
    REVERSE_CODE = chr(5)
    FORWARDS = chr(0)
    BACKWARDS = chr(1)
    # break text by newline
    textLines = text.split('\n')

    # assume we are starting forwards
    outputText = '' 
    goingForwards = True
    headLocation = 0
    for idx,line in enumerate(textLines):
        outputText += line
        # remove non-printing characters for length
        # calculation (e.g., bold, underline, etc.)
        # all characters below 31 are non-printing
        line = ''.join([x for x in line if ord(x) > 31])
        if goingForwards:
            headLocation += len(line)
        else:
            headLocation -= len(line)
        # now, we do math to figure out where the
        # printhead should go
        if idx < len(textLines)-1: # nothing for last line
            nextLineLen = len(textLines[idx+1])
            # go in the direction closest to one end
            diff = nextLineLen - headLocation
            if diff > headLocation:
                # too close to beginning, so just
                # go back to the beginning and
                # print forwards
                outputText += REVERSE_CODE + FORWARDS + chr(headLocation) + BACKWARDS
                #               rev code^  print dir^   num spaces^          ^ spaces are backwards
                headLocation = 0
                goingForwards = True
            else:
                # go to end of the line, and print backwards
                if diff < 0: # forward spaces
                    # note: diff can't be bigger than 255
                    outputText += REVERSE_CODE + BACKWARDS + chr(-diff) + FORWARDS
                else:
                    outputText += REVERSE_CODE + BACKWARDS + chr(diff) + BACKWARDS
                headLocation = nextLineLen
                goingForwars = False
    return outputText

MAXLINE = 40
# if HARDCODED_PORT is '', then the user will get a choice
HARDCODED_PORT = '/dev/tty.wchusbserial1420'

if len(sys.argv) == 1:
    print("Usage:\n\ttextToBean filename [port choice]")
    quit()

filePath = sys.argv[1]
if len(sys.argv) > 2:
    portChoiceInt = int(sys.argv[2])
else:
    portChoiceInt = 0
# choose port
if HARDCODED_PORT == '':
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
else:
    portChoice = HARDCODED_PORT

# read entire file so we can parse for markdown
with open(filePath, "r") as f:
    allText = f.read()

# parse markdown, only looking for __text__ for underline
# and **text** for bold
remainingText = parseMarkdown(allText)

# add reversing
remainingText = placeReverses(remainingText)
print(remainingText)
quit()

# set up serial port
ser = serial.Serial(portChoice, 115200, timeout=0.1)
# wait a bit
time.sleep(2)

# get the file length
fileLen = os.path.getsize(filePath)

# first two bytes are the file length (max: 65K)
# sent in little-endian format
stringHeader = chr(0x00) + chr(fileLen & 0xff) + chr(fileLen >> 8)

try:
        # read MAXLINE characters at a time and send
    while len(remainingText) > 0:
        chars = remainingText[:MAXLINE]
        remainingText = remainingText[MAXLINE:]
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
