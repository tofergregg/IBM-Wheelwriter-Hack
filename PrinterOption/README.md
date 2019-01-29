This is information for the Wheelwriter 10/15 printer option card, which has a parallel port interface.

First, set up the printer using CUPS to be a raw printer, called "WheelwriterUSB"

To print a file:

lpr -P "WheelwriterUSB" file.txt

The printer needs both a line feed and a carriage return to get to the beginning of a line (e.g., 0xa0xd). To produce this in vim in insert mode, type ctrl-v ctrl-M to put in the extra carriage return.

To add carriage returns to all lines in vim:

`:%s/$/\^V^M/g`

(replace ^V^M with actual ctrl-V ctrl-M)

To do so automatically for unix-style text files:

`cat test.txt | gsed -z 's/\n/\r\n/g' | lpr -P WheelwriterUSB`

The printer interface accepts some EPSON escape codes. See http://stanislavs.org/helppc/epson_printer_codes.html for details.

For example:

"ESC E" (no spaces) turns bold on and "ESC F" turns bold off.
"ESC - 1" (no spaces) turns underlining on and "ESC - 0" turns underline off.

Known codes that work:
  bold (emphasis) 
  underline
  superscript/subscript


