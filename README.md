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
* The first pulse is always a throwaway 0, indicating that someone is going to write 9 more bits to the bus.
