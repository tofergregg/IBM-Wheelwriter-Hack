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

def eraseSector(sectorNum):
    '''Sectors are 4096 byte regions. 
    To erase a sector, we load the following bytes:
    0xAA at 0x5555
    0x55 at 0x2AAA
    0x80 at 0x5555
    0xAA at 0x5555
    0x55 at 0x2AAA
    0x30 at sectorNum, where sectorNum is a number between 0 and 32, and 
    needs to be shifted into bits 16 to 12'''
    print("Erasing sector {}, bytes {}-{}".format(sectorNum,sectorNum*4096,sectorNum*4096+4095))
    GPIO.output(WE, 0)
    GPIO.output(OE, 0)
    GPIO.output(CE, 1)
    GPIO.output(WE, 1)

    for a,d in ((0x5555, 0xAA), (0x2AAA, 0x55), (0x5555, 0x80), (0x5555, 0xAA), (0x2AAA, 0x55), ((sectorNum << 12), 0x30)):
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

def printDataRow(row, startAddr, dataOffset):
    '''Prints out a row of data mimicing the way "hexdump -C file" does, e.g.:
        000000c0                    0b ff  76 05 ff 76 03 b0 02 e8        |..v..v....|
        000000d0  1b 06 b8 59 02 50 8d 06  c0 01 50 e8 f3 01 0b c0  |...Y.P....P.....|
        000000e0  74 03 e9 5d 01 a0 80 06  88 46 09 80 26 81 06 19  |t..].....F..&...|
        000000f0  c6 06 89 01 01 c7 06 da  07 00 00 c7 06 dc 07 00  |................|
        00000100  00 c7 06 de 07 00 00 c6  06 e0 07 40 c6 06 e2 07  |...........@....|
        00000110  00 1e 1e 8d 3e 12 07 8d  36 59 76 0e 1f 07 fc b9  |....>...6Yv.....|
        00000120  20 00 f3 a5 1f 83 ec 06  ff 76 05 ff 76 03 2a c0  | ........v..v.*.|
        00000126  ec 06 ff 76 05 ff 76 03  2a c0 9a 8e              |...v..v.*...|
       There are three types of lines:
       1. A line that starts at an address after an address divided by a multiple of 16
       2. A line that starts at an address divisible by a multiple of 16 with 16 bytes
       3. A line that starts at an address divisible by a multple of 16 with fewer than 16 bytes
   
       Variables:
       row: an array of 1-16 bytes
       startAddr: the divisible-by-16 start address for the line
       dataOffset: the offset from startAddr where the actual data starts

       The easiest thing to do is going to be to pad the row with -1s
    '''
    # pad before start
    for i in range(dataOffset):
        row.insert(0,-1)

    # pad after start
    for i in range(16-len(row)):
        row.append(-1)
    
    print("{:08x}  ".format(startAddr), end='')

    for b in row[:8]:
        if b != -1:
            print("{:02x} ".format(b),end='')
        else:
            print("   ",end='')

    print(" ",end='')

    for b in row[8:]:
        if b != -1:
            print("{:02x} ".format(b),end='')
        else:
            print("   ",end='')

    foundStart = False
    for c in row:
        if c == -1 and not foundStart:
            print(" ",end='')
            continue
        if not foundStart:
            print("|",end='')
            foundStart = True

        if c == -1:
            break

        if c < 32 or c > 126:
            print('.',end='')
        else:
            print(chr(c),end='')

    print("|")
    
def readData(startAddr, endAddr, verbose=False):
    '''Will read all data from startAddr to endAddr, inclusive,
    and will return in an array of bytes'''

    # printDataRow([0,1,2,3,4,5,6,7,8,9,10],0,5)
    # printDataRow([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],0,0)
    # printDataRow([4,5,6,7,8,9,10],0,0)
    # printDataRow([4,5,6,7,8,9,10],0,4)
    allData = []
    for i, addr in enumerate(range(startAddr, endAddr + 1)):
        d = readByte(addr)
        #import pdb; pdb.set_trace()

        allData.append(d)
        if (((i + startAddr + 1) % 16 == 0 or i + startAddr == endAddr) and verbose): 
            if (i + startAddr == endAddr):
                # make startP the next lowest multiple of 16 minus 1
                # based on code found here: https://www.geeksforgeeks.org/round-to-next-greater-multiple-of-8/
                startP = i & -16
                printDataRow(allData[startP:],startP+startAddr,0)
            elif len(allData) < 16:
                # if we are at the beginning
                startP = 0 
                printDataRow(allData[startP:],i-15+startAddr,16 - len(allData))

            else:
                startP = i - 15
                printDataRow(allData[startP:],startP+startAddr,0)

        elif not verbose:
            # print amount every 1K
            if (i + 1) % 1024 == 0:
                print("{}K, ".format((i + 1) // 1024), end='')
                sys.stdout.flush()
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
    parser_write.add_argument('--diff-with', '-d', help='Only write the differences from this file')

    # create the parser for the "erase" command
    parser_erase = subparsers.add_parser('erase', help='Erases sectors on the chip, or the entire chip')
    parser_erase.add_argument('--chip', '-c', action='store_true', help='Erase the entire chip')
    parser_erase.add_argument('--sectors', '-s', metavar = 'sectorNum', nargs='*', help='Erase the sectors listed, with each sector a 4096 byte section of the chip')

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

def writeSector(sector, data):
    '''Erases the sector on the the chip, then writes the 4096 bytes in data to the same sector'''
    if len(data) != 4096:
        print("Each sector needs 4096 bytes, and the data passed in has a length of {} bytes.".format(len(data)))
    else:
        eraseSector(sector)
        startAddr = 4096 * sector
        for i,d in enumerate(data):
            if not programByte(i + startAddr, d):
                print("Write failed at address {}!".format(i + startAddr))
                return
       
def writeFileDiffToChip(filename, diffFile):
    with open(filename, "rb") as f:
        fileText = f.read()
    with open(diffFile, "rb") as f:
        chipText = f.read()
    if len(fileText) != len(chipText):
        print("Both files must be the same size.")
    else:
        # determine which sectors will need to be erased
        sectorsToModify = set()
        for i, (b1, b2) in enumerate(zip(fileText,chipText)):
            if b1 != b2:
                sectorsToModify.add(i // 4096)

        print("Sectors to modify: {}".format(list(sectorsToModify))) 
        for sector in sectorsToModify:
            print("Writing sector {}".format(sector))
            writeSector(sector,fileText[sector * 4096:(sector + 1) * 4096])
            


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

        elif args['command'] == 'write':
            if args['diff_with']:
                print("Writing data in '{}' that is not in '{}' to the chip.".format(args['filename'],args['diff_with']))
                print("(This assumes that '{}' is the data already on the chip)".format(args['diff_with']))
                writeFileDiffToChip(args['filename'],args['diff_with'])
            else:
                print("Writing '{}' to the chip.".format(args['filename']))
                writeFileToChip(args['filename'])
            
        elif (args['command'] == 'erase'):
            if args['sectors'] and len(args['sectors']) > 0:
                sectors = [int(x) for x in args['sectors']]
                print("Are you SURE you want to erase sector{} ".format('' if len(sectors) == 1 else 's'),end='')
                for i,s in enumerate(sectors):
                    print(s,end='')
                    if i < len(sectors) - 1:
                        print(", ",end='')
                ans = input("? Please type 'yes': ")
                if ans == "yes":
                    for s in sectors:
                        eraseSector(s)
                else:
                    print("Not erasing any sectors.")
            else:
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
