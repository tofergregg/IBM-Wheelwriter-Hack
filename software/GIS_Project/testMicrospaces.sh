#!/bin/bash

# 20 microspaces equals one regular space

# The following should print
# a b c d
# and then print it again on top of the old a b c d

./send_command.py reset
./send_command.py return

./send_command.py characters "a b c d"
./send_command.py return 0

./send_command.py characters "a" 0
./send_command.py movecursor 20 0

./send_command.py characters "b" 0
./send_command.py movecursor 20 0

./send_command.py characters "c" 0
./send_command.py movecursor 20 0

./send_command.py characters "d" 0
./send_command.py return 50

