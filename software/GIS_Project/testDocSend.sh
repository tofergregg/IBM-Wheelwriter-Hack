while read -r line; do 
    ./send_command.py characters "${line}"
    ./send_command.py return; 
done < testDocument.txt

