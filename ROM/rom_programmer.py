#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys
import traceback
import argparse

FULL_CHIP_SIZE = (1 << 17) # 128K

# datasheet: https://www.datasheets360.com/pdf/1277907997291200345?xrefPartId=1277907997291200345&alternatePartManufacturerId=0
# KM23C256 pins 

# datasheet for flash chip: http://ww1.microchip.com/downloads/en/DeviceDoc/20005022C.pdf
# Microchip SST39SF010A

#ADDR = [1,7,8,25,24,23,18,15,4,17,10,27,14,3,2]
ADDR = [1,7,8,25,24,23,18,15,4,17,10,27,14,3,2,26,19]
DATA = [12,16,20,13,6,5,0,11]
CE = 9
OE = 22
WE = 21

def setDataPins(val):
    '''Sets the DATA pins to val, which should be either
    GPIO.IN or GPIO.OUT'''
    for p in DATA:
        GPIO.setup(p, val)

def setupGPIO():
    GPIO.setmode(GPIO.BCM)

    # set address pins as output
    for p in ADDR:
        GPIO.setup(p, GPIO.OUT)

    # set CE, OE, and WE as output
    GPIO.setup(CE, GPIO.OUT)
    GPIO.setup(OE, GPIO.OUT)
    GPIO.setup(WE, GPIO.OUT)

def setAddress(n):
    '''Sets each pin in ADDR to its corresponding bit from n'''
    for i,p in enumerate(ADDR):
        GPIO.output(p, n & (1 << i))

def setData(d):
    '''Sets the data pins represented in DATA to the value of d'''
    setDataPins(GPIO.OUT)
    for i,p in enumerate(DATA):
        GPIO.output(p, (d >> i) & 0b1)

def readByte(addr):
    '''Returns the byte read from address addr'''
    setDataPins(GPIO.IN)
    GPIO.output(CE, 0)
    GPIO.output(OE, 0)
    GPIO.output(WE, 1)
    setAddress(addr)

    # read data
    d = 0
    for i,p in enumerate(DATA):
        d = d | (GPIO.input(p) << i)
    return d


def getChipId():
    '''Runs the "Software ID Entry" sequence, reads the value at address 0x0001, and then
    runs the "Software Exit" sequence to put the chip back into read mode.
    The following sequence is for Software ID Entry:
    0xAA at address 0x5555
    0x55 at address 0x2AAA
    0x90 at address 0x5555'''
    GPIO.output(OE, 0)
    GPIO.output(CE, 1)
    GPIO.output(WE, 1)

    for a,d in ((0x5555, 0xAA), (0x2AAA, 0x55), (0x5555, 0x90)):
        print("Setting address: %x, data: %x" % (a,d))
        setAddress(a)
        setData(d)
        GPIO.output(OE, 1)
        GPIO.output(CE, 0)
        GPIO.output(WE, 0)
        #time.sleep(100./1000000) 

        GPIO.output(WE, 1)
#        GPIO.output(OE, 0)
#        GPIO.output(CE, 1)
    GPIO.output(CE, 1)


    # Now we read location 0001 for the Device ID
    b = readByte(0x1)
    print("Device ID: %x\n" % b)

    # Now we peform the exit sequence. The easy way is to set the data to be 0xF0
    setData(0xF0)
    GPIO.output(OE, 1)
    GPIO.output(CE, 0)
    GPIO.output(WE, 0)
    time.sleep(100./1000000) 

    GPIO.output(WE, 1)
    GPIO.output(OE, 0)
    GPIO.output(CE, 1)

def programByte(addr, data):
    '''Programs a byte at addr (must be 0xFF to begin, meaning that the sector or chip  must have been 
    erased at some point prior to the write. To write, we first send a set of three bytes:
    0xAA at address 0x5555
    0x55 at address 0x2AAA
    0xA0 at address 0x5555
    Then we send byte at addr, and then we check DQ7 until it reads the correct value at least three times
    ''' 
    MAX_DATA_READS = 10
    # import pdb; pdb.set_trace()

    GPIO.output(OE, 0)
    GPIO.output(CE, 1)
    GPIO.output(WE, 1)

    for a,d in ((0x5555, 0xAA), (0x2AAA, 0x55), (0x5555, 0xA0), (addr, data)):
        # print("Setting address: %x, data: %x" % (a,d))
        setAddress(a)
        setData(d)
        GPIO.output(OE, 1)
        GPIO.output(CE, 0)
        GPIO.output(WE, 0)
        time.sleep(100./1000000) 

        GPIO.output(WE, 1)
        #GPIO.output(OE, 0)
        #GPIO.output(CE, 1)

    # now read DQ7 until we get three bits that equal data & 0b10000000
    # if we read 10 times without a success, we have a problem
    setDataPins(GPIO.IN)
    d7Val = (data & 0b10000000) >> 7
    numCorrect = 0
    for i in range(MAX_DATA_READS):
        # print("Checking %d: %d" % (i,d7Val))
        if (GPIO.input(DATA[7]) == d7Val):
            numCorrect += 1
        else:
            numCorrect = 0
        if numCorrect == 3:
            break
        if i == MAX_DATA_READS - 1:
            return False

    GPIO.output(WE, 0)
    GPIO.output(CE, 0)
    GPIO.output(OE, 1)
    return True

def eraseChip():
    '''To erase the chip, we load the following bytes:
    0xAA at 0x5555
    0x55 at 0x2AAA
    0x80 at 0x5555
    0xAA at 0x5555
    0x55 at 0x2AAA
    0x10 at 0x5555'''
    GPIO.output(WE, 0)
    GPIO.output(OE, 0)
    GPIO.output(CE, 1)
    GPIO.output(WE, 1)

    for a,d in ((0x5555, 0xAA), (0x2AAA, 0x55), (0x5555, 0x80), (0x5555, 0xAA), (0x2AAA, 0x55), (0x5555, 0x10)):
        print("Setting address: %x, data: %x" % (a,d))
        setAddress(a)
        setData(d)
        GPIO.output(OE, 1)
        GPIO.output(CE, 0)
        GPIO.output(WE, 0)

        GPIO.output(WE, 1)
        GPIO.output(OE, 0)
        GPIO.output(CE, 1)
    # sleep for 2 seconds to ensure chip is erased
    time.sleep(2)


def readData(startAddr, endAddr, verbose=False):
    '''Will read all data from startAddr to endAddr, inclusive,
    and will return in an array of bytes'''

    allData = []
    for i, addr in enumerate(range(startAddr, endAddr + 1)):
        d = readByte(addr)
        #import pdb; pdb.set_trace()

        if (verbose): 
            print(hex(d), end=' ')
            sys.stdout.flush()
        else:
            # print amount every 1K
            if (i + 1) % 1024 == 0:
                print("{}K, ".format((i + 1) // 1024), end='')
                sys.stdout.flush()
        allData.append(d)
    if verbose:
        print()
    else:
        print("Done!")
    allData = bytes(allData)
    return allData

def parseArgs():
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser._action_groups.pop()

    subparsers = parser.add_subparsers(help='sub-command help',dest='command')

    # create the parser for the "read" command
    parser_read = subparsers.add_parser('read', help='read -h')
    parser_read.add_argument('readVals', metavar = 'No value or startAddr endAddr', nargs='*', help='No values will read entire chip, or two values to read from startAddr to endAddr, inclusive. E.g., "rom_programmer read 0 15" will read the 16 bytes from address 0 to address 15.')
    parser_read.add_argument('--filename', '-o', help='File to write contents to.')
    parser_read.add_argument('--verbose', '-v', action='store_true', help='Print all values to the terminal (in hex).')

    # create the parser for the "write" command
    parser_write = subparsers.add_parser('write', help='write -h')
    parser_write.add_argument('filename', help='Will erase entire chip and write the contents of filename to the chip.')

    # create the parser for the "erase" command
    parser_write = subparsers.add_parser('erase', help='Erases the chip')

    return vars(parser.parse_args())

def writeFileToChip(filename):
    ans = input("Erasing chip before writing -- are you SURE you want to erase the chip? Type 'yes': ")
    if ans != "yes":
        print("Not writing to chip.")
    else:
        eraseChip()
        with open(filename, "rb") as f:
            fileText = f.read()
        bytesToWrite = FULL_CHIP_SIZE if len(fileText) > FULL_CHIP_SIZE else len(fileText)
        print("Will write {} bytes to the chip.".format(bytesToWrite))
        for addr in range(bytesToWrite):
            if not programByte(addr, fileText[addr]):
                print("Write failed at address {}!".format(addr))
                return
            if (addr + 1) % 1024 == 0:
                print("{}K, ".format((addr + 1) // 1024), end = '')
                sys.stdout.flush()
        print("Done!")
        

if __name__ == "__main__":
    args = parseArgs()
    setupGPIO()
    try:
        if (args['command'] == 'read'):
            print("Reading from the chip")
            readValsLen = len(args['readVals'])
            if readValsLen == 0:
                # read entire chip
                print("Reading entire chip ({}KB).".format(FULL_CHIP_SIZE // 1024))
                allData = readData(0,FULL_CHIP_SIZE-1, args['verbose'])
            elif readValsLen == 2:
                # read values, which could be in hex
                val1Str = args['readVals'][0]
                if val1Str.startswith('0x'):
                    addr1 = int(val1Str,16) # base 16
                else:
                    addr1 = int(val1Str) # base 10
                
                val2Str = args['readVals'][1]
                if val2Str.startswith('0x'):
                    addr2 = int(val2Str,16) # base 16
                else:
                    addr2 = int(val2Str) # base 10

                print("Reading {} bytes, from address {:02x} to address {:02x}.".format(addr2 - addr1 + 1, addr1, addr2))
                allData = readData(addr1, addr2, args['verbose'])

            else:
                print('Must have either 0 or 2 values for read (0 means "read entire chip")')
                quit()
            if args['filename']:
                print("Writing output to {}.".format(args['filename']))
                with open(args['filename'],"wb") as f:
                    f.write(allData)

        elif (args['command'] == 'write'):
            print("Writing '{}' to the chip.".format(args['filename']))
            writeFileToChip(args['filename'])
            
        elif (args['command'] == 'erase'):
            ans = input("Are you SURE you want to erase the entire chip? Please type 'yes': ")
            if ans == 'yes':
                print("Erasing the chip")
                eraseChip()
            else:
                print("Not erasing the chip.")

    except KeyboardInterrupt:
        print("Keyboard interrupt...")
    except:
        print("Error or exception occurred.")
        traceback.print_exc()
    finally:
        GPIO.cleanup()
