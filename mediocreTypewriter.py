#!/usr/bin/env python

import serial,readchar,sys,time,threading,Queue

# define a function that will be run in a thread and will
# read character input and buffer it
def readChars(q):
    t = threading.currentThread()
    while getattr(t,"do_run", True):
        key = readchar.readchar()
        q.put(key)

# setup serial 
ser = serial.Serial('/dev/cu.LightBlue-Bean', 57600, timeout=0.5)
# wait a bit
time.sleep(0.5)

q = Queue.Queue()

if __name__ == "__main__":
    t = threading.Thread(target=readChars,args=(q,))
    num = 0;
    print("Please start typing! (ctrl-c or ctrl-d to quit, ctrl-g for bell)")
    t.start()
    while True:
        if (not q.empty()):
            key = q.get()
            if (key == '\r'):
                print('\r')
            else:
                if key != '\x07': # ignore bell for terminal
                    sys.stdout.write(key)
                    sys.stdout.flush()
            if key == '\x03' or key == '\x04': # ctrl-c or ctrl-d
                t.do_run = False
                print("\r\nPress a key to stop.\r")
                t.join()
                break
            ser.write(key)
        time.sleep(0.1)
    print("Cleaning up!")
    ser.close()
