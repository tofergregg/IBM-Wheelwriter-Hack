#!/usr/bin/env python

from PIL import Image
import sys

if len(sys.argv) != 2:
    print("Usage:\n\t./imageTest image")
    quit()

im = Image.open(sys.argv[1])
im = im.convert('RGB')

#im_rgb = Image.new("RGB", im.size, (255, 255, 255))
#im_rgb.paste(im, mask=im.split()[3]) # 3 is the alpha channel

b = im.tobytes()

b2 = ''
for idx,byte in enumerate(b):
    if ord(byte) < 150:
        b2 += chr(0)
    else:
        b2 += chr(255)

im2 = Image.frombytes('RGB',(im.width,im.height),b2)
for r in range(0,im2.height*3,3):
    for c in range(0,im2.width*3,3):
        #print(ord(b2[r * im2.width + c]))
        #print(r,c)
        if (ord(b2[r * im2.width + c]) == 0):
            sys.stdout.write('.')
        else:
            sys.stdout.write(' ')
    sys.stdout.write('\n')

im2.show()
