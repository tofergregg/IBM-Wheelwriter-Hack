This README file describes the python scripts located in this folder.

`textWithSpaces.py`:
* usage:<p>
`./textWithSpaces.py "text to print" [microspacing] [serialPort]`

* description:<p>
Prints the text on the typewriter with the desired microspacing between characters. 0 microspaces will print one character on top of the other, and 10 microspaces is normal spacing for 12pica font.<p>
The optional `microspacing` argument will default the microspacing to 10.<p>
The optional `serialPort` argument will set the serial port. Otherwise, users can choose from available ports (unless there is only one available port, which will be chosen automatically).

* notes:<p>
The typewriter does not automatically produce a newline after this command.

`moveCursor.py`:
* usage:<p>
`./moveCursor.py horizontal vertical [serialPort]`

* description:<p>
Moves the cursor `horizontal` number of microspaces horizontally and `vertical` number of microspaces vertically. Either parameter can be be negative. A positive horizontal number moves to the *right*, and a positive vertical number moves *down*.

* notes:<p>
The typewriter will attempt to move the cursor, but behavior is undefined if the cursor reaches the ends of the platen.

`returnCursor.py`:
* usage:<p>
`./returnCursor.py [serialPort]`

* description:<p>
Attempts to return the cursor to the beginning of the line, based on an internal count of microspaces. 

* notes:<p>
When printing, the Arduino attempts to keep track of the position of the cursor, but this doesn't always work (e.g., if someone manually types on the keyboard). You should use `resetTypewriter.py` (see below) at the beginning of a session.

`resetTypewriter.py`:
* usage:<p>
`./resetTypewriter.py [serialPort]`

* description:<p>
Resets the typewriter, and clears the microspace count.

* notes:<p>
None
