#!/bin/bash

./send_command.py reset
./send_command.py return
./send_command.py characters 'the quick ' 10
./send_command.py characters 'brown fox ' 8
./send_command.py characters 'jumps over the ' 6
./send_command.py characters ' lazy dog' 15
./send_command.py return
./send_command.py movecursor 50 0
./send_command.py characters "some more text"
./send_command.py movecursor 0 20

./send_command.py characters 'Four score and seven years ago our fathers brought forth on this continent a new nation, conceived in liberty,'
./send_command.py return 20
./send_command.py characters 'and dedicated to the proposition that all men are created equal.'
./send_command.py return 5

./send_command.py characters 'Now we are engaged in a great civil war,' 15
./send_command.py return
./send_command.py characters 'testing whether that nation or any nation' 8
./send_command.py return
./send_command.py characters 'so conceived and so dedicated, can long endure.'
./send_command.py return
./send_command.py characters '..........' 1
for i in `seq 1 10`; do
    ./send_command.py movecursor 0 1
    ./send_command.py characters '.' 0
done

for i in `seq 1 10`; do
    ./send_command.py movecursor -1 0
    ./send_command.py characters '.' 0
done

for i in `seq 1 10`; do
    ./send_command.py movecursor 0 -1
    ./send_command.py characters '.' 0
done

./send_command.py movecursor 0 200

