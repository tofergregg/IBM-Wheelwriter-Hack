#!/bin/bash

./send_command.py reset
./send_command.py return

# print a box, slowly
./send_command.py characters '..........' 1
./send_command.py movecursor -1 0
for i in `seq 1 10`; do
    ./send_command.py movecursor 0 1
    ./send_command.py characters '.' 0
done

for i in `seq 1 9`; do
    ./send_command.py movecursor -1 0
    ./send_command.py characters '.' 0
done

for i in `seq 1 10`; do
    ./send_command.py movecursor 0 -1
    ./send_command.py characters '.' 0
done

./send_command.py movecursor 0 200

