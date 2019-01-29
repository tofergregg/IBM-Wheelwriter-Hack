#!/usr/bin/env python3

import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:\n\t{} [rom.bin]".format(sys.argv[0]))
        quit()
    with open(sys.argv[1],"rb") as f:
        romData = f.read()

    while True:
        try:
            byteAddr = int(input(),0)
            print(hex(romData[byteAddr]))
        except EOFError:
            break 

