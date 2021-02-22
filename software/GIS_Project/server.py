#!/usr/bin/env python3

import socket
import sys
import os
import json
import time
import serial
import availablePorts
import argparse

DATA_AMOUNT = 1024
MAXLINE = 40

def getArgs():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
   
    parser.add_argument('-p','--port',type=int,default=10000,dest='port',help="the socket port, defaults to 10000")
    parser.add_argument('serial_port',default=None,nargs='?',help="the serial port, e.g., '/dev/tty.wchusbserial1410'")
    return vars(parser.parse_args())

def sendBytes(ser, bytesToSend):
    try:
        ser.write(bytesToSend.encode())
        response = ""
        while True:
            response += ser.read(10).decode('utf-8')
            #print("resp:"+response)
            if len(response) > 0 and response[-1] == '\4':
                response = response[:-1] # remove 0x04
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
    print("Moving cursor %d microspaces horizontally and %d microspaces vertically" % (horizontal, vertical))
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
    return response 

def resetTypewriter(ser):
    print("Resetting typewriter...")
    bytesToSend = chr(0x04) 
    response = sendBytes(ser, bytesToSend)

    #response = "Typewriter reset."
    print(response)
    return response

def returnCursor(ser,vertical):
    print("Returning cursor...")
    if vertical < 0:
        vertical += 65535 + 1 # two's complement conversion
    vb0 = vertical & 0xff # little byte
    vb1 = (vertical >> 8) & 0xff # big byte

    bytesToSend = chr(0x06) + chr(vb0) + chr(vb1)
    response = sendBytes(ser, bytesToSend)

    #response="Returned cursor to beginning of line."
    print(response)
    return response

def getMicrospaces(ser):
    print("Getting microspace count...")
    bytesToSend = chr(0x08)
    response = sendBytes(ser, bytesToSend)

    #response="Returned cursor to beginning of line."
    print(response)
    return response

def sendCharacters(ser, stringToPrint, spacing):
    print('Sending "%s" with spacing %d...' % (stringToPrint,spacing))
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
            if len(stringToPrint) > 0:
                #print("sleeping")
                #print("to print: " + stringToPrint)
                time.sleep(3) # wait for characters to print
            #sys.stdout.write(chars)
            #sys.stdout.flush()
        response = ""
        while True:
            response += ser.read(10).decode('utf-8')
            # print("resp:"+response)
            if len(response) > 0 and response[-1] == '\4':
                response = response[:-1] # remove '\4' 
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    print("response: ")
    print(response)
    return response

def runServer(ser,port):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', port)
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
                data = connection.recv(DATA_AMOUNT).decode('utf-8')
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
                        reply = returnCursor(ser,args['vertical'])
                    elif args['command'] == 'characters':
                        st = args['string_to_print']
                        if len(st) > 0:
                            reply = sendCharacters(ser, st,args['spacing'])
                        else:
                            reply = "Empty string, no characters sent."
                    elif args['command'] == 'microspaces':
                        reply = getMicrospaces(ser)
                    else:
                        reply = "not a known command"
                    print("about to sendall")
                    connection.sendall(reply.encode())
                    print("finished sendall")
                    # print('sending "%s" to typewriter' % args)
                    print("about to sendall again")
                    connection.sendall('\0'.encode())
                    print("finished sendall again")
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

def setupSerial(portChoice):
    print("Setting up...")
    # if HARDCODED_PORT is '', then the user will get a choice
    #HARDCODED_PORT = '/dev/tty.wchusbserial1410'
    HARDCODED_PORT = ''

    # choose port
    if portChoice == None:
        portChoiceInt = 0
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
    args = getArgs()
    try:
        ser = setupSerial(args['serial_port'])
        runServer(ser,args['port'])
    except Exception as ex:
         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
         message = template.format(type(ex).__name__, ex.args)
         print(message)
    finally:
        print("Closing serial connection.")
        ser.close()

