#!/usr/bin/env python3

import sys

TIME_DIV = 10000

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:\n\tletterConversion.py filename.csv")
        quit()

    for filename in sys.argv[1:]:
        allLines = []
        sys.stdout.write(filename+":\n")
        with open(filename) as f:
            # read header
            header = f.readline()[:-1].split(",")
            header = [x[1:-1] for x in header]
            for line in f.readlines():
                allLines.append(line[:-1].split(","))

        #print(allLines)

        pulses = [] 
       
        bitCount = 0 # ignore first bit, and we will be looking for 9 bits
        bitString = ''
        ignoreOnes = False
        for idx in range(1,len(allLines[1:])): # ignore first set of zeroes
            if ignoreOnes:
                ignoreOnes = False
                continue
            t0 = float(allLines[idx][0])*1e6 # relative time diffs
            t1 = float(allLines[idx+1][0])*1e6
            diff = t1-t0
            numBits = round(diff / 5.25) # five time slices per clock
            bitValue = int(allLines[idx][1])
            #sys.stdout.write(str(numBits)+":" )
            for i in range(numBits):
                if bitCount == 0:
                    # this bit should always be a 0
                    bitCount += 1
                    continue # ignore the zero sentinel
                #sys.stdout.write(str(bitValue)+" ")
                bitString = str(bitValue)+bitString
                bitCount += 1
                if (bitCount == 10):
                    bitCount = 0
                    #sys.stdout.write(' : ')
                    print('sendByteOnPin(0b'+str(bitString)+');')
                    print('delayMicroseconds(200);')
                    print('// wait for response of 0b000000000')
                    print()
                    bitString = ''
                    if numBits < 7 or bitValue == 0: # 7 is a guess for now
                        ignoreOnes = True
                    break
            # now ignore the next set of 1s
        print()

