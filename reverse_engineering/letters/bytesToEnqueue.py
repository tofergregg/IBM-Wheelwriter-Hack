#!/usr/bin/env python3

import sys

# will read in bytes in a stream like this:
# filename.csv: 100100001 : 000000000 : 000000011 : 000000000 : 000001000 : 000000000 :

# the goal is to take all the even bytes (starting with the 0th) 
# and put them into the following form:
# q.enqueue(0b100100001);

line = sys.stdin.readline()

line = line[line.find(': ')+2:-1]
allBytes = line.split(' : ')[:-1]

for idx,b in enumerate(allBytes):
    if idx % 2 == 0:
        print('q.enqueue(0b'+b+');')

