This README file describes the python scripts located in this folder.

Becuase the typewriter Arduino gets reset each time a serial connection is made, the system is set up with a server and client, with the server maintaining a continuous serial connection with the Arduino. This has the added benefit of being relatively fast -- commands can be sent one after the other using the `send_command.py` program.

`server.py`:
* usage:<p>
`./server.py [-h] [-p PORT] [serial_port]`

* description:<p>
Runs the server for the Wheelwriter control. This should be run in its own window, and should stay running while commands are sent. The server waits for a command that is sent from the `send_command.py` program (see below).

* notes:<p>
The server attempts to connect on port 10000 as a default. If the `-p` flag is used, another port is tried.
If the `serial_port` option is left off, the user is given a choice of ports, unless there is only one choice available.

`send_command.py`:
* usage:<p>
`./send_command.py [-h] {characters,return,reset,movecursor,microspaces} ...`

* description:<p>
Sends a command to the server, which forwards it to the typewriter.  
The following commands are available:
  * `characters`:<p>
    * usage:<p>
    `./send_command.py characters [-h] string_to_print [spacing]`

    * description:<p>
    Prints the `string_to_print` (e.g., `"This is some text"`) on the typewriter with `spacing` microspaces between characters. Ten microspaces is regular text, and 10 is the default.

    * notes:<p>
    The typewriter attempts to keep track of the total number of microspaces that have been used on a line so far. When the `return` command is used, the typewriter backs up this number of microspaces. See the `microspaces` command below to determine the number of microspaces that the typewriter has counted. 

  * `return`:<p>
    * usage:<p>
    `./send_command.py return [-h] [vertical]`

    * description:<p>
    Sends the typewriter cursor back to the beginning of the line, based on an internal count of microspaces that have happened so far. See the `microspaces` command below to determine the number of microspaces that the typewriter has counted. The default value for `vertical` is 16 microspaces, which is normal one-line linespacing. The `vertical` argument can be positive (down), negative (up), or zero to simply move the cursor to the beginning of the line.

    * notes:<p>
    The number of microspaces may not be correct, but usually is. A mistake can occur if someone types something on the typewriter keyboard after already typing something, or if the server is stopped and restarted (which resets the number of microspaces to zero). See the `reset` command below to guarantee moving the cursor to the beginning of the line.

  * `reset`:<p>

    * usage:<p>
    `./send_command.py reset [-h]`

    * description:<p>
    Sends a reset command to the typewriter, which returns the cursor to the beginning of the line (but does not advance the paper vertically).

    * notes:<p>
    The `reset` command is not fast, and it also resets the daisy wheel. However, it should always return the cursor to the beginning of the line.

  * `movecursor`:<p>
    * usage:<p>
    `./send_command.py movecursor [-h] horizontal vertical`

    * description:<p>
    Moves the cursor horizontally and vertically a given number of microspaces. A positive `horizontal` value is to the right, and a negative value is to the left. A positive `vertical` value is down, and a negative value is up. E.g., `./send_command.py movecursor 100 40` will move the cursor 100 microspaces to the right, and 40 microspaces down. Ten horizontal microspaces is normal text, and sixteen vertical microspaces is a line-spacing of one.
    
    * notes:<p>
      * Both horizontal and vertical arguments must be given, but either can be 0. For example, `./send_command.py movecursor 0 10` advances down by ten microspaces, but does not move horizontally.
      * The internal number of microspaces for a line is updated for any horizontal cursor movement.

  * `microspaces`:<p> 
    * usage:<p>
    `./send_command.py microspaces [-h]

    * description:<p>
    Prints the number of microspaces that the typewriter thinks have occurred so far on a line.
    * notes:<p>
    None.
