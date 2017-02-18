#!/bin/bash
./textToNano.py text_examples/hitchBegin.txt
./sendImageNano.py ../../images/moog25.png
sleep 3
./textToNano.py text_examples/moog.txt
sleep 3
./textToNano.py text_examples/formattingTest.txt
