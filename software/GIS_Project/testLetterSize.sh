#!/bin/bash

# 20 microspaces equals one regular space

./send_command.py reset

# sends 101 characters (should be the full 8.5in width) at the 
# regular 10 microspaces per character
./send_command.py characters "01234567891123456789212345678931234567894123456789512345678961234567897123456789812345678991234567891"
./send_command.py return

./send_command.py characters "A period at the beginning and end of the paper:"
./send_command.py return
./send_command.py characters "." 0
./send_command.py movecursor 1000 0
./send_command.py characters "." 0
./send_command.py return

exit 0
# send 10 * 100 = 1000 periods, spaced 1-microspace apart
for i in `seq 1 10`; do
    echo "sending 100 periods at 1-microspace per period"
    ./send_command.py characters "...................................................................................................." 1
done

./send_command.py return
