if [ -z "$1" ]
  then
    printf "\tusage: $0 filename.txt\n"
    exit -1
fi

while IFS= read -r line; do 
    ./send_command.py characters -m -- "${line}"
    ./send_command.py return; 
done < $1 
