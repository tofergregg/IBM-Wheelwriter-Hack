#!/usr/bin/env python

import socket
import sys
import os
import json
import time
import serial
import availablePorts

DATA_AMOUNT = 1024
MAXLINE = 40

def sendBytes(ser, bytesToSend):
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
    except Exception as ex:
        print("Exception in sendBytes.")
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
    return response

def moveCursor(ser, horizontal, vertical):
    # The horizontal and vertical microspaces are capped at +-32767
    # If either value is negative, we will convert it to two's complement
    # which will be easy to read on the Arduino
    #
    # We will convert each value to a 2-byte value in little endian 
    # format to transfer

    if horizontal < 0:
        horizontal += 65535 + 1 # two's complement conversion
    hb0 = horizontal & 0xff # little byte
    hb1 = (horizontal >> 8) & 0xff # big byte

    if vertical < 0:
        vertical += 65535 + 1 # two's complement conversion
    vb0 = vertical & 0xff # little byte
    vb1 = (vertical >> 8) & 0xff # big byte

    bytesToSend = chr(0x05) + chr(hb0) + chr(hb1) + chr(vb0) + chr(vb1) 

    response = sendBytes(ser, bytesToSend)
    #response = "Moved cursor %d horizontal microspaces and %d vertical microspaces." % (horz,vert)
    print(response)
    return response 

def resetTypewriter(ser):
    bytesToSend = chr(0x04) 
    response = sendBytes(ser, bytesToSend)

    #response = "Typewriter reset."
    print(response)
    return response

def returnCursor(ser):
    bytesToSend = chr(0x06)
    response = sendBytes(ser, bytesToSend)

    #response="Returned cursor to beginning of line."
    print(response)
    return response

def getMicrospaces(ser):
    bytesToSend = chr(0x08)
    response = sendBytes(ser, bytesToSend)

    #response="Returned cursor to beginning of line."
    print(response)
    return response

def sendCharacters(ser, stringToPrint, spacing):
    # get the text length
    textLen = len(stringToPrint) 

    # first two bytes are the file length (max: 65K)
    # sent in little-endian format
    stringHeader = chr(0x00) + chr(textLen & 0xff) + chr(textLen >> 8) + chr(spacing)

    try:
        # read MAXLINE characters at a time and send
        while len(stringToPrint) > 0:
            chars = stringToPrint[:MAXLINE]
            stringToPrint = stringToPrint[MAXLINE:]
            if chars == '':
                break
            ser.write(bytearray(stringHeader + chars,'utf-8'))
            stringHeader = ''  # not needed any more
            #sys.stdout.write(chars)
            #sys.stdout.flush()
            response = ""
            while True:
                response += ser.read(10).decode('utf-8')
                #print("resp:"+response)
                if len(response) > 0 and response[-1] == '\n':
                    print("response: ")
                    break
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    #response='Typed "%s" with spacing %d.' % (string_to_print, spacing)
    print(response)
    return response

def runServer(ser):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 10000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print('Ready to receive commands!')
        print('Waiting for a connection')
        connection, client_address = sock.accept()
        fullData = ''
        try:
            print('connection from %s port %s' % client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(DATA_AMOUNT)
                if data:
                    # print('received "%s"' % data)
                    fullData += data
                else:
                    print('no more data from %s port %s' % client_address)
                    args = json.loads(fullData)
                    if args['command'] == 'movecursor':
                        reply = moveCursor(ser, args['horizontal'],args['vertical'])
                    elif args['command'] == 'reset':
                        reply = resetTypewriter(ser)
                    elif args['command'] == 'return':
                        reply = returnCursor(ser)
                    elif args['command'] == 'characters':
                        reply = sendCharacters(ser, args['string_to_print'],args['spacing'])
                    elif args['command'] == 'microspaces':
                        reply = getMicrospaces(ser)
                    else:
                        reply = "not a known command"
                    connection.sendall(reply)
                    # print('sending "%s" to typewriter' % args)
                    connection.sendall('\0')
                    break
        except Exception as ex:
            print("Exception in runServer.") 
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
        finally:
            # Clean up the connection
            connection.close()
            print

def setupSerial():
    print("Setting up...")
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
    return ser

if __name__ == '__main__':
    try:
        ser = setupSerial()
        runServer(ser)
    except Exception as ex:
         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
         message = template.format(type(ex).__name__, ex.args)
         print(message)
    finally:
        print("Closing serial connection.")
        ser.close()
