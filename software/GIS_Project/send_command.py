#!/usr/bin/env python2.7
# coding=utf-8

# note: if you are on linux, you might have to run
# with sudo
# If you don't want to run with sudo, you can try
# adding dialout to your user (requires a logout to
# take effect:
#    $ sudo usermod -a -G dialout $USER

import os
import sys
import argparse
import socket
import json
from time import sleep as sleep
import errno

DATA_AMOUNT = 1024

def getArgs():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser._action_groups.pop()
 
    subparsers = parser.add_subparsers(help='sub-command help',dest='command')

    # create the parser for the "characters" command
    parser_a = subparsers.add_parser('characters', help='characters help')
    parser_a.add_argument('string_to_print', help='e.g., "this is some text"')
    parser_a.add_argument("spacing", type=int, default=10, nargs='?', help="e.g., 12 (default is 10)")

    # create the parser for the "return" command
    parser_b = subparsers.add_parser('return', help='return help')
    parser_b.add_argument("vertical", type=int,default=16, nargs='?', help="e.g., 10 (default is 16)")

    # create the parser for the "reset" command
    parser_c = subparsers.add_parser('reset', help='reset help')

    # create the parser for the "movecursor" command
    parser_d = subparsers.add_parser('movecursor', help='movecursor help')
    parser_d.add_argument("horizontal", type=int, help="horizontal microspaces, positive is right, negative is left, e.g. 10")
    parser_d.add_argument("vertical", type=int, help="vertical microspaces, positive is down, negative is up, e.g., -10")

    # create the parser for the "reset" command
    parser_e = subparsers.add_parser('microspaces', help='prints the number of horizontal microspaces so far on a line')
    
    return vars(parser.parse_args())

def setup_connection():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    # sys.stderr.write('connecting to %s port %s\n' % server_address)
    sock.connect(server_address)
    return sock

def send_command(args):
    sock = setup_connection()

    try:
        # Send data
        message = json.dumps(args) 
        # sys.stderr.write('sending "%s"\n' % message)
        sock.sendall(message)
        sock.shutdown(socket.SHUT_WR)

        # Look for the response
        # Response should be null-terminated

        sock.setblocking(0)
        done = False
        while True:
            try:
                data = sock.recv(DATA_AMOUNT)
                if len(data) > 0:
                    if data[-1] == '\0':
                        done=True
                        data = data[:-1]
                    print("Received: %s\n" % data)
                    if done:
                        break
                sleep(0.25)
            except socket.error as serr:
                sleep(0.25)
                if serr.errno != errno.EAGAIN:
                    raise serr

    finally:
        # sys.stderr.write('closing socket\n')
        sock.close()

if __name__ == "__main__":
    args = getArgs()
    if args['command'] == "characters":
        print('Typing "%s" with spacing %d.' % (args['string_to_print'],args['spacing']))
    elif args['command'] == "return":
        print('Returning cursor to beginning of line.')
    elif args['command'] == "reset":
        print('Reseting typewriter.')
    elif args['command'] == "movecursor":
        # note: 10 microspaces horizontally is normal spacing
        #       and 8 microspaces vertically is 1 line spacing
        print('Moving cursor %d microspaces horizontally and %d microspaces vertically.' % (args['horizontal'],args['vertical']))
    elif args['command'] == "microspaces":
        print("Querying for current number of microspaces.")
    send_command(args)

