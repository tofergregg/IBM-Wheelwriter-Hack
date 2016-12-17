# IBM-Wheelwriter-Hack
Turning an IBM Wheelwriter into a unique printer

This project has three goals:

1. Electronically connect an Arduino to an IBM Wheelwriter 6 (will probably work for other models) to emulate the IBM printer option card when using a custom driver.
2. Allow someone to type directly to the typewriter from a computer keyboard, through a computer.
3. Add fun options, e.g., raster printing (!) at a low dpi through the use of micro-up/down and micro-backspace. (If I can figure out the code to send a micro-forward space, that would be nice, too...)

The IBM Wheelwriter, circa 1984, is an electronic typewriter with a beautiful Model M keyboard and a daisy-wheel print head. The typewriter is (not suprisingly, given that it is an IBM) built like a tank, and the PCBs are exceedingly well laid out and annotated, and easy to access. The case pops off with a bit of elbow grease, and there is an expansion port on one of the two PCBs with labeled pins. Yay!

The only pins we really care about are "bus" and ground, although eventually we'll care about 5V when we attach the Arduino and want to power it from the typewriter itself.

Reverse-engineering the bus has been an interesting two-week endeavor (so far). The tools necessary: an Arduino (I'm using a Light Blue Bean+) and a logic analyzer. The initial logic analyzer I used was a Bus Pirate, but unfortunately the BP does not have enough memory to capture some of the longer sequences of commands (e.g., a carriage return). So, a colleague loaned me a Saleae 8-pin logic analyzer, which has worked great (though it does have some quirks).

So far (as of 17 Dec 2016), I have successfully reverse engineered printing characters and carriage returns. Here is the basic idea for sending a command on the bus:

* Pulse period: 5.25us
* Number of pulses sent per command: 10 (an "I'm writing to the bus" to begin, and nine more bits)
* Normal state of the bus: high (5V), and devices sending commands must pull the bus to low for a zero, and leave high for a one.
* The first pulse is always a throwaway 0, indicating that a device is going to write 9 more bits to the bus.
* The next nine bits are (as far as I can tell) in LSB order. Commands seem to always start with 0b100100001 (which is sent right-most bit first). I originally thought the commands were MSB first, but when I was reverse engineering the carriage-return command the numbers came out such that it looks like it is LSB. This makes reading the logic traces in the reverse order from the numeric bit pattern. Maybe I should have kept the MSB ordering in the code because it is easier for humans to read, but I switched it to make it consistent with the way the typewriter expects commands.
* When a device sends its 10 bits on the bus, there is almost always a response from the motor driver PCB (that's what I'm calling it), and this response is usually a 10-byte zero (a 52.5us zero pulse, basically). We need to look for this response before sending the next 10-bit value in our command.
* The reason I am somewhat hesitant to declare the MSB/LSB debate finished is because the character table is completely whacky. It is not ASCII, and it isn't any of the EBCDIC variations I've tracked down. You might think that there would be some method to it, but I haven't yet figured it out. The table below is what I have so far; as you can see, the characters A, B, C have character codes 0x20, 0x12, and 0x1b. I have a feeling that the codes might be based off of the keyboard scan codes, but I haven't found the pattern yet.

<pre>
int asciiTrans[128] = 
//col: 0     1     2     3     4     5     6     7     8     9     a     b     c     d     e     f     row:
    {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 0

//    
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // 1
     
//    sp     !     "     #     $     %     &     '     (     )     *     +     ,     -     .     /
     0x00, 0x49, 0x4b, 0x38, 0x37, 0x39, 0x3f, 0x4c, 0x23, 0x16, 0x36, 0x3b, 0xc, 0x0e, 0x57, 0x28, // 2
     
//     0     1     2     3     4     5     6     7     8     9     :     ;     <     =     >     ?
     0x30, 0x2e, 0x2f, 0x2c, 0x32, 0x31, 0x33, 0x35, 0x34, 0x2a ,0x4e, 0x50, 0x00, 0x4d, 0x00, 0x4a, // 3

//     @     A     B     C     D     E     F     G     H     I     J     K     L     M     N     O
     0x3d, 0x20, 0x12, 0x1b, 0x1d, 0x1e, 0x11, 0x0f, 0x14, 0x1F, 0x21, 0x2b, 0x18, 0x24, 0x1a, 0x22, // 4

//     P     Q     R     S     T     U     V     W     X     Y     Z     [     \     ]     ^     _
     0x15, 0x3e, 0x17, 0x19, 0x1c, 0x10, 0x0d, 0x29, 0x2d, 0x26, 0x13, 0x41, 0x00, 0x40, 0x00, 0x4f, // 5
     
//     `     a     b     c     d     e     f     g     h     i     j     k     l     m     n     o
     0x00, 0x01, 0x59, 0x05, 0x07, 0x60, 0x0a, 0x5a, 0x08, 0x5d, 0x56, 0x0b, 0x09, 0x04, 0x02, 0x5f, // 6
     
//     p     q     r     s     t     u     v     w     x     y     z     {     |     }     ~    DEL
     0x5c, 0x52, 0x03, 0x06, 0x5e, 0x5b, 0x53, 0x55, 0x51, 0x58, 0x54, 0x00, 0x00, 0x00, 0x00, 0x00}; // 7
</pre>

To send commands to the typewriter, we connect one pin of the Arduino to the bus through a MOSFET transistor. When we set this pin high, the bus is pulled low, indicating a zero that we want to send. We capture other devices commands with a different Arduino pin that reads the raw state of the bus.

The hardest part about making the commands work is that there isn't a clock on the bus, and all commands must be timed for as close to 5.25us pulses as we can get. The Arduino is *just* barely fast enough to do this, and you have to resort to directly writing to the PORTD (or PORTB) pin registers and reading from the PIND (or PINB) registers to hit the tolerances. I.e., you can't use digitalWrite() or digitalRead() -- the commands are just too slow. The highest granularity timer we have access to on the Arduino (without going super-duper low-level) is `delayMicroseconds()`, which can come close enough to 5.25us to work, but it takes a bit of fiddling to get right. I will eventually port the code to an Arduino proper, but on the Light Blue Bean+, the tolerances don't have any wiggle room. Side note: the LBB+ has some internal ports rearranged, so PORTD and PORTB do not map to the standard Arduino pins. I've noted that in the code where necessary, and I will ifdef the proper pins when I convert to a normal Arduino.


