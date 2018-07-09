/*
  IBM Wheelwriter hack
  Pin 0: connected through MOSFET to Wheelwriter bus
         Will pull down the bus when set to zero
  Pin 2: ALSO connected to the bus, but listens instead of 
         sending data
 */

#include <EEPROM.h>

#define LETTER_DELAY 450
#define CARRIAGE_WAIT_BASE 200
#define CARRIAGE_WAIT_MULTIPLIER 15

bool bold = false; // off to start
bool underline = false; // off to start
bool reverseText = false; // for printing in reverse
int LED = 13; // the LED light

// on an Arduino Nano, ATmega328, the following will delay roughly 5.25us
#define pulseDelay() { for (int i=0;i<16;i++) { __asm__ __volatile__("nop\n\t"); } }

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

int microspaceCount = 0;

void setup() 
{
  // initialize serial communication at 115200 bits per second:
  Serial.begin(115200);
  Serial.setTimeout(25);
  
  // Digital pins
  pinMode(2,OUTPUT); // pin that will trigger the bus
  pinMode(3, INPUT); // listening pin
  pinMode(4, INPUT_PULLUP); // for the button

  pinMode(LED, OUTPUT);
  
  // start the input pin off (meaning the bus is high, normal state)
  PORTD &= 0b11111011;

  //resetTypewriter(); // Arduino resets whenever a new serial connection is made...
  //microspaceCount = readMicrospacesFromEEPROM();

}

// the loop routine runs over and over again forever:
void loop() 
{
      static int charCount = 0;
      static int microspaceCount = 0;
      unsigned char buffer[70]; // 64 plus a few extra for some run-over commands (e.g., reverse)
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
          // 2: Toggle Bold
          // 3: Toggle Underline
          // 4: Reset typewriter
          // 5: TBA
          // 6: TBA
          // 7: Beep typewriter (traditional 0x07 beep char)
          // If the byte is >= 5, just treat as one character
          bytesRead = Serial.readBytes(buffer, 1);
          digitalWrite(LED,1);
          //Serial.print("Read ");
          //Serial.println(bytesRead);
          //Serial.println(" bytes.");
          char command = buffer[0];
          //Serial.println(int(command));
          
          if (command == 0) { // text to print
            // look for next two bytes
            Serial.readBytes(buffer,3);
            bytesToPrint = buffer[0] + (buffer[1] << 8); // little-endian
            int spacing = buffer[2];
            microspaceCount = microspaceCount + bytesToPrint * spacing;
            //writeMicrospacesToEEPROM(microspaceCount);
            Serial.print("microspaceCount: ");
            Serial.println(microspaceCount);
            charCount = printAllChars(buffer,bytesToPrint,charCount, spacing);
          }
          else if (command == 1) { // image to print
            //Serial.println("image");
            printImage(buffer);
          } else if (command == 2) {
            bold = !bold; // toggle
            Serial.println("ok");
          } else if (command == 3) {
            underline = !underline;
            Serial.println("ok");
          } else if (command == 4) {
            // reset the typewriter so we know we are on the begining of a line
            resetTypewriter();
            //writeMicrospacesToEEPROM(0);
            microspaceCount = 0;
            bold = underline = reverseText = false;
            Serial.println("reset");
          } else if (command == 5) {
            // position cursor horizontally and vertically from current position
            // we expect four more bytes, as follows:
            // byte 0: little end of 2-byte horizontal value
            // byte 1: big end of 2-byte horizontal value
            //
            // byte 2: little end of 2-byte vertical value
            // byte 3: big end of 2-byte vertical value

            // Negative values will be in two's complement format for 16-bit int values
            
            Serial.readBytes(buffer,4);
            int horizontal = buffer[0] + (buffer[1] << 8); // little-endian

            int vertical = buffer[2] + (buffer[3] << 8); // little endian

            moveCursor(horizontal,vertical);
            microspaceCount += horizontal;
            Serial.println("moved cursor by " + String(horizontal) + 
                " horizontal microspaces and " + String(vertical) + " vertical microspaces");
          } else if (command == 6) {
            // returns the cursor to the beginning of the line, based on microspaceCount
            // also moves the cursor vertically by the amount given in the next two bytes
            Serial.readBytes(buffer,2);
            int vertical = buffer[0] + (buffer[1] << 8); // little endian
            
            moveCursor(-microspaceCount, vertical);
            Serial.print("sent cursor to beginning of line with ");
            Serial.print(-microspaceCount);
            Serial.println(" microspaces");
            //writeMicrospacesToEEPROM(0);
            microspaceCount = 0;
          } else if (command == 7) {
            beepTypewriter(); 
            Serial.println("ok");
          } else if (command == 8) {
            // report on microspaceCount
            Serial.print("microspaceCount: ");
            Serial.println(microspaceCount);
          }
          else {
            charCount = printOne(command,charCount);
          }
          digitalWrite(LED,0); // turn off LED when we are finished processing
      }
      // button for testing
      byte button = digitalRead(4);
      if (button == 0) {
        //printOne("a",1);   
        //paper_vert(1,1);
        //micro_backspace(25);
        //paper_vert(1,100);
        //forwardSpaces(5);
        //fastText("this is really fast");
        //send_letter(0b000000001); // 'a'
        //send_letter(0b001011001); // 'b'
        //send_letter(0b000000100); // 'm'
        //send_letter();
        digitalWrite(13,1); // led
        delay(100);
        digitalWrite(13,0);    
        resetTypewriter(); 
      }
      delay(10);
}

int printOne(int charToPrint, int charCount) {
    // print the character, and return the number of chars on the line that are left.
    // E.g., if we start with 6 and we print a character, then we return 7.
    // But, if we print a return, then that clears the charCount to 0, and if we
    // go left by one, that subtracts it, etc.

    if (charToPrint < 0) {
      charToPrint += 256; // correct for signed char
    }

    if (charToPrint == '\r' or charToPrint == '\n') {
        send_return(charCount);
        charCount = 0;
    }
    else if (charToPrint == 128 or charToPrint == 129) {
        paper_vert((charToPrint == 128 ? 0 : 1),8); // full line up/down
    }
    else if (charToPrint == 133) { // micro-down, ctrl-d is 4
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
    else if (charToPrint == 132) { // micro-forwardspace
        // DOES NOT UPDATE CHARCOUNT!
        // THIS WILL CAUSE PROBLEMS WITH RETURN!
        // TODO: FIX THIS ISSUE
        forwardSpaces(1);
    }
    else {
        //Serial.println("about to print");
        //send_letter(asciiTrans[charToPrint]);
        send_letter_without_space(asciiTrans[charToPrint]);

        charCount++;
    }
    
    Serial.println("ok"); // sends back our characters (one) printed
    Serial.flush();
    delay(10);
    //Bean.setLed(255, 0, 0);
    //Bean.sleep(10);
    //Bean.setLed(0,0,0);
    return charCount;
}

int printAllChars(char buffer[], 
                  uint16_t bytesToPrint, 
                  int charCount, int spacing) {
    uint8_t readLength = 65;
    bool fastPrinting = false;
    uint16_t bytesPrinted = 0;
    uint8_t bufferPos = 0;
    uint8_t bytesRead = 0;
    
    while (bytesToPrint > 0) {
        // read bytes from serial
        //Serial.print("about to print ");
        //Serial.print(bytesToPrint);
        //Serial.println(" bytes");
        bytesPrinted = 0;
        // wait for more bytes, but only wait up to 5 seconds
        unsigned long startTime = millis();
        bool timeout = false; 
        while (not Serial.available() and not timeout) {
          if (millis() - startTime > 5000) {
            timeout = true;
          }
          delay(10);
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
        //Serial.println(bytesRead);
        bufferPos = 0;
        while (bufferPos < bytesRead) {
          // print all the bytes
          // check for underline and bold
          if (buffer[bufferPos] == 2) { // bold
              bold = !bold;
          }
          else if (buffer[bufferPos] == 3) { // underline
              underline = !underline;
          }
          else if (buffer[bufferPos] == 5) { // reverse instruction
              // we might need to read in more of the command, which
              // is four bytes long
              int bytesToRead = 4 - (bytesRead - bufferPos);
              while (bytesToRead > 0) {
                  // read necessary bytes
                  int extraBytesRead = Serial.readBytes(buffer+bytesRead, bytesToRead);
                  bytesRead += extraBytesRead;
                  bytesToRead -= extraBytesRead;
              }
              // now we have enough bytes
              int print_dir = buffer[bufferPos+1];
              int numSpaces = buffer[bufferPos+2];
              int spacesDir = buffer[bufferPos+3];
              bufferPos += 4;
              // 
          }
          else if (buffer[bufferPos] != '\r' and buffer[bufferPos] != '\n') {
                // begin fast printing
                if (!fastPrinting) {
                    fastTextInit();
                    fastPrinting = true;
                }
                fastTextChars(buffer + bufferPos, 1, spacing);

                if (reverseText) {
                    charCount--;
                    if (charCount < 0) {
                      charCount = 0;
                    }
                } else {
                    charCount++;
                }
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

void printImage(char *buffer) {
    // will read 3-tuples of bytes
    // first byte is low-order byte for run length,
    // second byte is high-order byte for run length,
    // third byte is the byte to print (typically, period, space, or return)
    uint32_t rowBitsPrinted = 0;
    int bitsRead = 0;
    
    while (1) { // keep reading bytes until we get (0,0,0)
        // read bytes from serial
        // wait for more bytes, but only wait up to 2 seconds
        unsigned long startTime = millis();
        bool timeout = false;
        bool first = true;
        while (Serial.available() == 0 and not timeout) {
          if (first) {
            Serial.println("Please send.");
            first = false;
          }
          if (millis() - startTime > 2000) {
            timeout = true;
          }
          delay(50);
          //Bean.sleep(10);
        }
        if (timeout) {
            paper_vert(1,1);
            Serial.println("timeout");
            micro_backspace(rowBitsPrinted * 3);
            break;
        }
        bitsRead = Serial.readBytes(buffer, 3);
        //Serial.println(bitsRead); // should always be 3
        if (buffer[0] == 0 and buffer[1] == 0 and buffer[2] == 0) {
          Serial.println("end received");
          break; // no more bits to print
        }
        // we do have a run to print
        uint16_t runLength = buffer[0] + (buffer[1] << 8);
        printRun(runLength,buffer[2]);
    }
    Serial.println("done");
}

void printRun(uint16_t runLength, char c) {
    static bool inFastText = false;
    if (c == '\n') {
      fastTextFinish();
      //delay(LETTER_DELAY);
      paper_vert(1,1); // Move down one pixel
      if (runLength > 0) {
          micro_backspace(runLength * 3);
      }
      inFastText = false;
    }
    else {
      if (c == ' ') {
        // turn off fastText if it is on
        if (inFastText) {
          fastTextFinish();
          inFastText = false;
        }
        forwardSpaces(runLength);

      } else if (!inFastText) {
        fastTextInit();
        inFastText = true;
        fastTextCharsMicro(c,runLength);

      }
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
    pulseDelay(); // fudge factor for 5.75

    // send low order bit (LSB endian)
    int nextBit = (command & 0b000000001);
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay(); 
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      pulseDelay(); // special shortened...
    }
    
    // next bit (000000010)
    nextBit = (command & 0b000000010) >> 1;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }
    
    // next bit (000000100)
    nextBit = (command & 0b000000100) >> 2;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }
    
    // next bit (000001000)
    nextBit = (command & 0b000001000) >> 3;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }

    // next bit (000010000)
    nextBit = (command & 0b000010000) >> 4;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }


    // next bit (000100000)
    nextBit = (command & 0b000100000) >> 5;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1){
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }
    
    // next bit (001000000)
    nextBit = (command & 0b001000000) >> 6;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1) {
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }

    // next to last bit (010000000)
    nextBit = (command & 0b010000000) >> 7;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay();
    } else if (nextBit == 1){
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
    }

    // final bit (100000000)
    nextBit = (command & 0b100000000) >> 8;
    if (nextBit == 0) {
      // turn on
      PORTD |= 0b00000100;
      pulseDelay(); // last one is special :)
    } else if (nextBit == 1){
      // turn off
      PORTD &= 0b11111011;
      pulseDelay();
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
    if (underline) {
      sendByte(0b000000000); // no space
      sendByte(0b100100001);
      sendByte(0b000001011);
      sendByte(0b100100001);
      sendByte(0b000000011);
      sendByte(asciiTrans['_']);
    }
    if (bold) {
      sendByte(0b000000001); // one microspace
      sendByte(0b100100001);
      sendByte(0b000001011);
      sendByte(0b100100001);
      sendByte(0b000000011);
      sendByte(letter);
      sendByte(0b000001001);
    } else {
      // not bold
      sendByte(0b000001010); // spacing for one character
    }
    //delay(LETTER_DELAY); // before next character
}

void send_letter_without_space(int letter) {
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000000011);
    sendByte(letter);
    if (underline) {
      sendByte(0b000000000); // no space
      sendByte(0b100100001);
      sendByte(0b000001011);
      sendByte(0b100100001);
      sendByte(0b000000011);
      sendByte(asciiTrans['_']);
    }
    if (bold) {
      sendByte(0b000000001); // one microspace
      sendByte(0b100100001);
      sendByte(0b000001011);
      sendByte(0b100100001);
      sendByte(0b000000011);
      sendByte(letter);
      sendByte(0b000001001);
    } else {
      // not bold
      sendByte(0b000000000); // spacing for one character
    }
    //delay(LETTER_DELAY); // before next character
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
  // 4 == micro-down (paper down)
  // 21 == micro-up (paper up)
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
  
  delay(LETTER_DELAY); // give it a bit more time
}

void paper_vert(int direction, int microspaces) {
    // 0 == up
    // 1 == down

    // can only send up to 127 at a time
    while (microspaces > 127) {
      sendByte(0b100100001);
      sendByte(0b000001011);
      sendByte(0b100100001);
      sendByte(0b000000101);
      //sendByte((direction << 7) | (microspaces << 1));
      sendByte((direction << 7) | 127);
  
      sendByte(0b100100001);
      sendByte(0b000001011);
      
      delay(LETTER_DELAY);
      microspaces -= 127;
    }
      sendByte(0b100100001);
      sendByte(0b000001011);
      sendByte(0b100100001);
      sendByte(0b000000101);
      sendByte((direction << 7) | microspaces);
      sendByte(0b100100001);
      sendByte(0b000001011);
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
    //delay(LETTER_DELAY / 10); // a bit more time
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

    /*if (numChars <= 23 || numChars >= 26) {*/
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

    /*} else if (numChars <= 25) {
        // not sure why this is so different
        sendByte(0b000001101);
        sendByte(0b000000111);
        sendByte(0b100100001);
        sendByte(0b000000110);
        sendByte(0b000000000);
        sendByte(numChars * 10);
        sendByte(0b100100001);
        // right now, the platten is moving, maybe?
    }*/
    
    sendByte(0b000000101);
    sendByte(0b010010000);

    /*
    sendByte(0b100100001);
    

    // send one more byte but don't wait explicitly for the response
    // of 0b001010000
    sendByteOnPin(0b000001011);*/

    // wait for carriage 
    //delay(CARRIAGE_WAIT_BASE + CARRIAGE_WAIT_MULTIPLIER * numChars);
}

void send_return_microspaces(int numSpaces) {
    // calculations for further down
    int byte1 = (numSpaces) >> 7;
    int byte2 = ((numSpaces) & 0x7f) << 1;
    
    sendByte(0b100100001);
    sendByte(0b000001011);
    sendByte(0b100100001);
    sendByte(0b000001101);
    sendByte(0b000000111);
    sendByte(0b100100001);

    /*if (numChars <= 23 || numChars >= 26) {*/
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

    /*} else if (numChars <= 25) {
        // not sure why this is so different
        sendByte(0b000001101);
        sendByte(0b000000111);
        sendByte(0b100100001);
        sendByte(0b000000110);
        sendByte(0b000000000);
        sendByte(numChars * 10);
        sendByte(0b100100001);
        // right now, the platten is moving, maybe?
    }*/
    
    sendByte(0b000000101);
    sendByte(0b010010000);

    /*
    sendByte(0b100100001);
    

    // send one more byte but don't wait explicitly for the response
    // of 0b001010000
    sendByteOnPin(0b000001011);*/

    // wait for carriage 
    //delay(CARRIAGE_WAIT_BASE + CARRIAGE_WAIT_MULTIPLIER * numChars);
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
    // 10 microspaces is one space

    // max is 255
    while (microspaces > 255) {
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
      sendByte(0xff);
      delay(LETTER_DELAY);
      microspaces -= 255;
      //sendByte(0b000000010);
    }
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
      sendByte(microspaces);
    /*
    sendByte(0b100100001);
    

    // send one more byte but don't wait explicitly for the response
    // of 0b000000100
    sendByteOnPin(0b000001011);*/
}

void forwardSpaces(int microspaces) {
    // ten microspaces is one real space
    // max is 255
    while (microspaces > 255) {
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
      sendByte(0xff);
      delay(LETTER_DELAY);
      microspaces-=255;
    }
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
      sendByte(microspaces);
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
        while (((PIND & 0b00001000) >> 3) == 1) {
          // busy
        }
        while (((PIND & 0b00001000) >> 3) == 0) {
          // busy
        }
        delayMicroseconds(LETTER_DELAY); // wait a bit before sending next char
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
void fastTextChars(char *s, int length, int spacing) {
    // letters start here
    for (int i=0; i < length; i++) {
        sendByte(0b100100001);
        sendByte(0b000000011);
    
        sendByte(asciiTrans[*s++]);

        if (underline) {
            sendByte(0b000000000); // no space
            sendByte(0b100100001);
            sendByte(0b000001011);
            sendByte(0b100100001);
            sendByte(0b000000011);
            sendByte(asciiTrans['_']);            
        }
        if (bold) {
            sendByte(0b000000001); // one microspace
            sendByte(0b100100001);
            sendByte(0b000001011);
            sendByte(0b100100001);
            sendByte(0b000000011);
            sendByte(asciiTrans[*(s-1)]);
            sendByte(0b000001001);
        }
        else {
            if (reverseText) {
                sendByte(0); // no forward space
                micro_backspace(0b1010); // full space back
            } else {
            // full space
            //sendByte(0b000001010);
            sendByte(spacing);
            }
        }
    }
}

void fastTextCharsMicro(char s, uint16_t length) {
    // letters start here
    if (s == ' ') {
      // just make a fast run of spaces
      sendByte(0b100100001);
      sendByte(0b000000011);
      sendByte(0b000000000);
      sendByte(0b11 * length);
    } else {
        for (uint16_t i=0; i < length; i++) {
            sendByte(0b100100001);
            sendByte(0b000000011);
        
            sendByte(asciiTrans[s]);
            sendByte(0b000000011); // 1 microspace
        }
    }
    //delay(LETTER_DELAY + LETTER_DELAY / 10 * length / 5);
}

void fastTextFinish() {
    sendByte(0b100100001);
    sendByte(0b000001001);
    sendByte(0b000000000);
    
    //delay(LETTER_DELAY * 2); // a bit more time
}

void resetTypewriter() {
  sendByte(0b100100001);
  sendByte(0b000000000);
  //sendByte(0b000100110); // receives this...
  sendByte(0b100100001);
  sendByte(0b000000001);
  sendByte(0b000100000);

  sendByte(0b100100001);
  sendByte(0b000001001);
  sendByte(0b000000000);
  sendByte(0b100100001);
  sendByte(0b000001101);
  sendByte(0b000010010);
  sendByte(0b100100001);
  sendByte(0b000000110);
  sendByte(0b010000000);
  sendByte(0b000000000);
  sendByte(0b100100001);
  sendByte(0b000001101);
  sendByte(0b000001001);
  sendByte(0b100100001);
  sendByte(0b000000110);
  sendByte(0b010000000);
  sendByte(0b000000000);
  sendByte(0b100100001);
  sendByte(0b000001010);
  sendByte(0b000000000);
  sendByte(0b100100001);
  sendByte(0b000000111);
  sendByte(0b100100001);
  sendByte(0b000001100);
  sendByte(0b000000001);
}

void beepTypewriter() {
  spin();
  // not currently working
  /*
  sendByte(0b100100001);
  sendByte(0b000001011);
  sendByte(0b100100001);
  sendByte(0b000001011);
  */
}

void moveCursor(int horizontal, int vertical) {
   // move horizontally first
   if (horizontal > 0) {
     forwardSpaces(horizontal);
   } else {
     micro_backspace(-horizontal);
   }

   // move vertically
   // (forgot why these commands are not symmetrical...)
   if (vertical > 0) {
    paper_vert(1,vertical);
   } else {
    paper_vert(0,-vertical);
   }
}

/*
int readMicrospacesFromEEPROM() {
    return EEPROM.read(0) + (EEPROM.read(1) << 8);
}

void writeMicrospacesToEEPROM(int m) {
    // write little endian to bytes 0,1
    EEPROM.update(0,m & 0xff);
    EEPROM.update(1,(m >> 8) & 0xff);
}
*/


