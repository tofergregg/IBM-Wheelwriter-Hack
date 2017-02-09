#!/usr/bin/env python3

import sys

TIME_DIV = 10000

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:\n\tletterConversion.py filename.csv")
        quit()

    for filename in sys.argv[1:]:
        allLines = []
        sys.stdout.write(filename+": ")
        with open(filename) as f:
            # read header
            header = f.readline()[:-1].split(",")
            header = [x[1:-1] for x in header]
            for line in f.readlines():
                allLines.append(line[:-1].split(","))

        #print(allLines)
        clockPeriod = int(allLines[0][2]) / TIME_DIV
#        print("Clock period: "+str(clockPeriod)+"ms")

        pulses = [] 
       
        bitCount = 1 # ignore first bit, and we will be looking for 9 bits
        ignoreOnes = False
        for idx in range(1,len(allLines[1:-1])): # ignore first set of zeroes
            if ignoreOnes:
                ignoreOnes = False
                continue
            t0 = int(allLines[idx][1]) # relative time diffs
            t1 = int(allLines[idx+1][1])
            diff = t1-t0
            numBits = round(diff / 5) # five time slices per clock
            bitValue = int(allLines[idx][3])
            #sys.stdout.write(str(numBits)+":" )
            for i in range(numBits):
                if bitCount == 0:
                    bitCount += 1
                    continue # ignore the zero sentinel
                sys.stdout.write(str(bitValue)+" ")
                bitCount += 1
                if (bitCount == 9):
                    bitCount = 0
                    sys.stdout.write(' : ') 
                    ignoreOnes = True
                    break
            # now ignore the next set of 1s
        print()

