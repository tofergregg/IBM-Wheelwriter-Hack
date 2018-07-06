This README file describes the python scripts located in this folder.

`textWithSpaces.py`:
* usage:<p>
`./textWithSpaces.py "text to print" microspacing [serialPort]`

* description:<p>
Prints the text on the typewriter with the desired microspacing between characters. 0 microspaces will print one character on top of the other, and 10 microspaces is normal spacing for 12pica font.<p>
The `serialPort` argument is optional, and users can choose from available ports without it (unless there is only one available port, which will be chosen automatically).

* notes:<p>
The typewriter does not automatically produce a newline after this command.



