/*
  IBM Wheelwriter hack
  Pin 0: connected through MOSFET to Wheelwriter bus
         Will pull down the bus when set to zero
  Pin 2: ALSO connected to the bus, but listens instead of 
         sending data
 */

#include<PinChangeInt.h>

static int d0 = 0;
static int d1 = 1;
static int d2 = 2;

#define LETTER_DELAY 170
#define CARRIAGE_WAIT_BASE 300
#define CARRIAGE_WAIT_MULTIPLIER 15

byte asciiTrans[128] = 
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
     
void setup() 
{
  // initialize serial communication at 57600 bits per second:
  Serial.begin(57600);

  Serial.setTimeout(25);
  
  // Digital pins
  pinMode(d0, OUTPUT);
  // because of Bean+ pin re-wiring, D0
  // is actually bit 3 in the DDRD and PORTD registers
  // start the pin high
  //PORTD |= 0b00000100;

  pinMode(d2, INPUT); // listening pin
  // PORTD |= 0b01000000; // the listening pin is mapped to bit 6

  // start the input pin off (meaning the bus is high, normal state)
  PORTD &= 0b11111011;
  pinMode(d1, INPUT_PULLUP);
}

// the loop routine runs over and over again forever:
void loop() 
{
      static int charCount = 0;
      char buffer[65];
      uint8_t readLength = 65;
      uint8_t bytesRead = 0;
      uint8_t bufferPos = 0;
      uint16_t bytesToPrint; 

      if (Serial.available() > 0) {
          // read one byte, and see if it is a command
          // Commands:
          // 0: next two bytes will be the number of characters we are going
          //    to send
          // 1: image bits (next two bytes will be the width and height)
          // 2: TBD
          // 3: TBD
          // If the byte is >= 4, just treat as one character
          bytesRead = Serial.readBytes(buffer, 1);
          //Serial.print("Read ");
         // Serial.println(bytesRead);
          //Serial.println(" bytes.");
          char command = buffer[0];
          if (command == 0) {
            // look for next two bytes
            Serial.readBytes(buffer,2);
            bytesToPrint = buffer[0] + (buffer[1] << 8); // little-endian
            charCount = printAllChars(buffer,bytesToPrint,charCount);
          }
          else if (command == 1) {
            Serial.readBytes(buffer,2);
            int width = buffer[0];
            int height = buffer[1];
            printImage(buffer, width, height);
          } else {
            charCount = printOne(command,charCount);
          }
      }
      // button for testing
      byte digital1 = digitalRead(d1);
      if (digital1 == 0) {
        paper_vert(1,1);
        micro_backspace(25);
        //paper_vert(1,100);
        //forwardSpaces(5);
        //fastText("this is really fast");
        //send_letter(0b000000001); // 'a'
        //send_letter(0b001011001); // 'b'
        //send_letter(0b000000100); // 'm'
        //send_letter();

        //print_str("aaaaaaaaaaaa");
        
        /*print_str("This is the symphony that schubert never finished!");
        send_return(50);

        print_str("\"the quick brown fox jumps over the lazy dog.\"");
        send_return(46);*/

        /*print_str("ABC");
        send_return(3);

        print_str("55555");
        send_return(5);

        print_str("1234567890");
        send_return(10);
        
        print_str("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
        send_return(26);

        print_str("1234567890");
        send_return(10);

        print_str(",./?");
        send_return(4);*/

        //print_str("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz");
        //send_return(52);

        //print_str("done.");
        //send_return(5);

        //print_strln("The quick brown fox jumps over the lazy dog.");
        /*
        sendByteOnPin(0b00000000);
        delayMicroseconds(60);*/
        /////////////
        //PORTD &= 0b11111011;
        Bean.setLed(255, 0, 0);
        Bean.sleep(10);
        Bean.setLed(0,0,0); 
      }
      Bean.sleep(10);  
}

int printOne(int charToPrint, int charCount) {
    // print the character, and return the number of chars on the line that are left.
    // E.g., if we start with 6 and we print a character, then we return 7.
    // But, if we print a return, then that clears the charCount to 0, and if we
    // go left by one, that subtracts it, etc.

    if (charToPrint < 0) {
      charToPrint += 256; // correct for signed char
      Serial.println(int(charToPrint));
    }

    if (charToPrint == '\r' or charToPrint == '\n') {
        send_return(charCount);
        charCount = 0;
    }
    else if (charToPrint == 128 or charToPrint == 129) {
        paper_vert((charToPrint == 128 ? 0 : 1),8); // full line up/down
    }
    else if (charToPrint == 4) { // micro-down, ctrl-d is 4
        paper_vert(1,1);
    }
    else if (charToPrint == 21) { // micro-up, ctrl-u is 21
        paper_vert(0,1);
    }
    else if (charToPrint == 130 or charToPrint == 0x7f) { 
        // left arrow or delete
        if (charCount > 0) {
            backspace_no_correct();
            charCount--;
        }
    }
    else if (charToPrint == 131) { // micro-backspace
        // DOES NOT UPDATE CHARCOUNT!
        // THIS WILL CAUSE PROBLEMS WITH RETURN!
        // TODO: FIX THIS ISSUE
        micro_backspace(1);
    }
    else {
        send_letter(asciiTrans[charToPrint]);
        charCount++;
    }
    
    Serial.println("ok"); // sends back our characters (one) printed
    Bean.setLed(255, 0, 0);
    Bean.sleep(50);
    Bean.setLed(0,0,0);
    return charCount;
}

int printAllChars(char buffer[], 
                  uint16_t bytesToPrint, 
                  int charCount) {
    uint8_t readLength = 65;
    bool fastPrinting = false;
    uint16_t bytesPrinted = 0;
    uint8_t bufferPos = 0;
    uint8_t bytesRead = 0;
    
    while (bytesToPrint > 0) {
        // read bytes from serial
        bytesPrinted = 0;
        // wait for more bytes, but only wait up to 2 seconds
        unsigned long startTime = millis();
        bool timeout = false; 
        while (Serial.available() == 0 and not timeout) {
          if (millis() - startTime > 2000) {
            timeout = true;
          }
          Bean.sleep(10);
        }
        if (timeout) {
          if (fastPrinting) {
            fastTextFinish();
            fastPrinting = false;
            send_return(charCount);
            charCount = 0;
          }
          break;
        }
        bytesRead = Serial.readBytes(buffer, readLength-1);
        Serial.println(bytesRead);
        bufferPos = 0;
        while (bufferPos < bytesRead) {
          // print all the bytes
          if (buffer[bufferPos] != '\r' and buffer[bufferPos] != '\n') {
                // begin fast printing
                if (!fastPrinting) {
                    fastTextInit();
                    fastPrinting = true;
                }
                fastTextChars(buffer + bufferPos, 1);
                charCount++;
          } else {
            if (fastPrinting) {
              fastTextFinish();
              fastPrinting = false;
            }
            send_return(charCount);
            charCount = 0;
          }
          bufferPos++;
          bytesToPrint--;
          bytesPrinted++;
        }
    }
    if (fastPrinting) {
      fastTextFinish();
    }
    Serial.println();
    return charCount;
}

void printImage(char buffer[], 
                  uint16_t width, uint16_t height) {
    uint32_t bitsToPrint = width * height;
    uint8_t readLength = 65;
    uint16_t bitsPrinted = 0;
    uint8_t bufferPos = 0;
    uint8_t bitsRead = 0;
    uint16_t colCount = 0;
    
    while (bitsToPrint > 0) {
        // read bytes from serial
        bitsPrinted = 0;
        // wait for more bytes, but only wait up to 2 seconds
        unsigned long startTime = millis();
        bool timeout = false; 
        while (Serial.available() == 0 and not timeout) {
          if (millis() - startTime > 2000) {
            timeout = true;
          }
          Bean.sleep(10);
        }
        if (timeout) {
            paper_vert(1,1);
            micro_backspace(width);
            break;
        }
        bitsRead = Serial.readBytes(buffer, readLength-1);
        Serial.println(bitsRead);
        bufferPos = 0;
        while (bufferPos < bitsRead) {
          // print all the bytes
          printBit(buffer[bufferPos]);
          colCount++;
          if (colCount == width) {
            paper_vert(1,1);
            micro_backspace(width);
            colCount = 0;
          }
          bufferPos++;
          bitsToPrint--;
          bitsPrinted++;
        }
    }
    Serial.println();
}

void printBit(char bit) {
    if (bit == 1) {
      letterMicrospace(asciiTrans['.']);
    }
    else {
      letterMicrospace(asciiTrans[' ']);
    }
}

void print_str(char *s) {
  while (*s != '\0') {
    send_letter(asciiTrans[*s++]);
  }
}

void print_strln(char *s) {
  // prints a line and then a carriage return
  print_str(s);
  send_return(strlen(s));
}

inline void sendByteOnPin(int command) {
    // This will actually send 10 bytes,
    // starting with a zero (always)
    // and then the next nine bytes
    
    // when the pin is high (on), the bus is pulled low
    noInterrupts(); // turn off interrupts so we don't get disturbed
    // unrolled for consistency, will send nine bits
    // with a zero initial bit
    // pull low for 5.75us (by turning on the pin)
    PORTD |= 0b00000100;
    delayMicroseconds(5); // fudge factor for 5.75

    // send low order bit (LSB endian)
    int nextBit = (command & 0b000000001);
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5); 
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(5 ); // special shortened...
    }
    
    // next bit (000000010)
    nextBit = (command & 0b000000010) >> 1;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }
    
    // next bit (000000100)
    nextBit = (command & 0b000000100) >> 2;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }
    
    // next bit (000001000)
    nextBit = (command & 0b000001000) >> 3;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }

    // next bit (000010000)
    nextBit = (command & 0b000010000) >> 4;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }


    // next bit (000100000)
    nextBit = (command & 0b000100000) >> 5;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1){
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }
    
    // next bit (001000000)
    nextBit = (command & 0b001000000) >> 6;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }

    // next to last bit (010000000)
    nextBit = (command & 0b010000000) >> 7;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(5);
    } else if (nextBit == 1){
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }

    // final bit (100000000)
    nextBit = (command & 0b100000000) >> 8;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      delayMicroseconds(6); // last one is special :)
    } else if (nextBit == 1){
      // turn off
      PORTD &= 0b11111011;
      delayMicroseconds(6 );
    }


    // make sure we aren't still pulling down
    PORTD &= 0b11111011;

    // re-enable interrupts
    interrupts();

}

void send_letter(int letter) {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000000011);
    sendByte(letter);
    sendByte(0b000001010);
    delay(LETTER_DELAY); // before next character
}

void letterNoSpace(int letter) {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000000011);
    sendByte(letter);
    sendByte(0); // don't send any spaces
    delay(LETTER_DELAY); // before next character
}

void letterMicrospace(int letter) {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000000011);
    sendByte(letter);
    sendByte(2); // send one microspace
    delay(LETTER_DELAY); // before next character
}

void paper_vert(int direction) {
  // 0 == up
  // 1 == down
  // 4 == micro-down
  // 21 == micro-up
  sendByte(0b100100001);
  sendByte(0b000001011);
  sendByte(0b100100001);
  sendByte(0b000000101);
  if (direction == 0) { // cursor-up (paper-down)
      sendByte(0b000001000);
  } else if (direction == 1) {
      sendByte(0b010001000); // cursor-down (paper-up)
  } else if (direction == 4) {
      sendByte(0b010000010); // cursor-micro-down (paper-micro-up)
  } else if (direction == 21) {
      sendByte(0b000000010); // cursor-micro-up (paper-micro-down)
  }
  sendByte(0b100100001);
  sendByte(0b000001011);
  
  delay(LETTER_DELAY * 2); // give it a bit more time
}

void paper_vert(int direction, int microspaces) {
    // 0 == up
    // 1 == down
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000000101);
    sendByte((direction << 7) | (microspaces << 1));
    
    sendByte(0b100100001);
    sendByte(0b000001011);
    delay(LETTER_DELAY + LETTER_DELAY * microspaces/5);
}

void backspace_no_correct() {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000100);
    sendByte(0b100100001);
    sendByte(0b000000110);
    sendByte(0b000000000);
    sendByte(0b000001010);
    /*sendByte(0b100100001);
    
  
    // send one more byte but don't wait explicitly for the response
    // of 0b000000100
    sendByteOnPin(0b000001011);*/
    delay(LETTER_DELAY * 2); // a bit more time
}

void send_return(int numChars) {
    // calculations for further down
    int byte1 = (numChars * 5) >> 7;
    int byte2 = ((numChars * 5) & 0x7f) << 1;
    
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000111);
    sendByte(0b100100001);
    
    if (numChars <= 23 || numChars >= 26) {
        sendByte(0b000000110);

        // We will send two bytes from a 10-bit number
        // which is numChars * 5. The top three bits
        // of the 10-bit number comprise the first byte,
        // and the remaining 7 bits comprise the second
        // byte, although the byte needs to be shifted
        // left by one (not sure why)
        // the numbers are calculated above for timing reasons
        sendByte(byte1);
        sendByte(byte2); // each char is worth 10
        sendByte(0b100100001);
        // right now, the platten is moving, maybe?

    } else if (numChars <= 25) {
        // not sure why this is so different
        sendByte(0b000001101);
        sendByte(0b000000111);
        sendByte(0b100100001);
        sendByte(0b000000110);
        sendByte(0b000000000);
        sendByte(numChars * 10);
        sendByte(0b100100001);
        // right now, the platten is moving, maybe?
    }
    
    sendByte(0b000000101);
    sendByte(0b010010000);

    /*
    sendByte(0b100100001);
    

    // send one more byte but don't wait explicitly for the response
    // of 0b001010000
    sendByteOnPin(0b000001011);*/

    // wait for carriage 
    delay(CARRIAGE_WAIT_BASE + CARRIAGE_WAIT_MULTIPLIER * numChars);
}

void correct_letter(int letter) {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000101);
    sendByte(0b100100001);
    sendByte(0b000000110);
    sendByte(0b000000000);
    sendByte(0b000001010);
    sendByte(0b100100001);
    sendByte(0b000000100);
    sendByte(letter);
    sendByte(0b000001010);
    sendByte(0b100100001);
    sendByte(0b000001100);
    sendByte(0b010010000);
}

void micro_backspace(int microspaces) {
    // 5 microspaces is one space
    sendByte(0b100100001);
    sendByte(0b000001110);
    sendByte(0b011010000);
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000100);
    sendByte(0b100100001);
    sendByte(0b000000110);
    sendByte(0b000000000);
    sendByte(microspaces << 1);
    delay(LETTER_DELAY + LETTER_DELAY * microspaces / 5);
    //sendByte(0b000000010);
    /*
    sendByte(0b100100001);
    

    // send one more byte but don't wait explicitly for the response
    // of 0b000000100
    sendByteOnPin(0b000001011);*/
}

void forwardSpaces(int num_microspaces) {
    // five microspaces is one real space
    sendByte(0b100100001);
    sendByte(0b000001110);
    sendByte(0b010010110);
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000110);
    sendByte(0b100100001);
    sendByte(0b000000110);
    
    sendByte(0b010000000);
    //sendByte(0b001111100);
    sendByte(num_microspaces << 1);
    delay(LETTER_DELAY);
}

void spin() {
    sendByte(0b100100001);
    sendByte(0b000000111);
}

void unknownCommand() {
    sendByte(0b100100001);
    sendByte(0b000001001);
    sendByte(0b010000000);
}

void sendByte(int b) {
        //Serial.println("sending byte!");
        sendByteOnPin(b);
        while (((PIND & 0b01000000) >> 6) == 1) {
          // busy
        }
        while (((PIND & 0b01000000) >> 6) == 0) {
          // busy
        }
        delayMicroseconds(5); // wait a bit before sending next char
}
void fastTextInit() {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001001);
    sendByte(0b000000000);
    sendByte(0b100100001);
    sendByte(0b000001010);
    sendByte(0b000000000);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000110);
    sendByte(0b100100001);
    sendByte(0b000000110);
    sendByte(0b010000000);
    sendByte(0b000000000);
    sendByte(0b100100001);
    sendByte(0b000000101);
    sendByte(0b010000000);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000010010);
    sendByte(0b100100001);
    sendByte(0b000000110);
    sendByte(0b010000000);
    sendByte(0b000000000);
}
void fastTextChars(char *s, int length) {
    // letters start here
    for (int i=0; i < length; i++) {
        sendByte(0b100100001);
        sendByte(0b000000011);
    
        sendByte(asciiTrans[*s++]);
        
        sendByte(0b000001010);
    }
}

void fastTextFinish() {
    sendByte(0b100100001);
    sendByte(0b000001001);
    sendByte(0b000000000);
    
    delay(LETTER_DELAY * 2); // a bit more time
}



