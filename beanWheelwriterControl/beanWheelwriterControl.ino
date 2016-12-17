/*
  IBM Wheelwriter hack
  Pin 0: connected through MOSFET to Wheelwriter bus
         Will pull down the bus when set to zero
  Pin 2: ALSO connected to the bus, but listens instead of 
         sending data
 */

#include<QueueArray.h>
#include<PinChangeInt.h>

static int d0 = 0;
static int d1 = 1;
static int d2 = 2;
static int d3 = 3;
static int d4 = 4;
static int d5 = 5;
static int d6 = 6;
static int d7 = 7;

#define LETTER_DELAY 150
#define CHAR_DELAY 150

QueueArray<int> q; // holds the bytes we will send to the bus

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

  // start the input pin off (meaning the bus is high, normal state)
  PORTD &= 0b11111011;
  pinMode(d1, INPUT_PULLUP);
}

// the loop routine runs over and over again forever:
void loop() 
{
  char buffer[64];
  size_t readLength = 64;
  uint8_t length = 0;  
         
      pinMode(d1, INPUT_PULLUP);  //PB1
      
      int digital1 = digitalRead(d1);
      if (digital1 == 0) {
        //send_letter(0b000000001); // 'a'
        //send_letter(0b001011001); // 'b'
        //send_letter(0b000000100); // 'm'
        //send_letter();

        //print_str("aaaaaaaaaaaa");
        
        /*print_str("This is the symphony that schubert never finished!");
        send_return(50);

        print_str("\"the quick brown fox jumps over the lazy dog.\"");
        send_return(46);*/

        print_str("testing");
        /*print_str("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
        send_return(26);

        print_str("1234567890");
        send_return(10);

        print_str(",./?");
        send_return(4);*/
        
        /*
        sendByteOnPin(0b00000000);
        delayMicroseconds(60);*/
        /////////////
        //PORTD &= 0b11111011;
        Bean.setLed(255, 0, 0);
        Bean.sleep(100);
        Bean.setLed(0,0,0); 
      }
      Bean.sleep(100);  
}

void print_str(char *s) {
  while (*s != '\0') {
    send_letter(asciiTrans[*s++]);
  }
}

void sendByteOnPin(int command) {
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
    q.enqueue(0b100100001);
    q.enqueue(0b000001011);
    q.enqueue(0b100100001);
    q.enqueue(0b000000011);
    q.enqueue(letter);
    q.enqueue(0b000001010);
    sendBytes();

    //delay(LETTER_DELAY); // before next character
}

void send_return(int numChars) {
    // calculations for further down
    int byte1 = (numChars * 5) >> 7;
    int byte2 = ((numChars * 5) & 0x7f) << 1;
    
    sendByteOnPin(0b100100001);
    //delayMicroseconds(200);
    delay(CHAR_DELAY);
    // wait for response of 0b000000000
    
    sendByteOnPin(0b000001011);
    delayMicroseconds(1450);
    // wait for response of 0b000000000
    
    sendByteOnPin(0b100100001);
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    sendByteOnPin(0b000001101);
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    sendByteOnPin(0b000000111);
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    sendByteOnPin(0b100100001);
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    if (numChars <= 23 || numChars >= 26) {
         sendByteOnPin(0b000000110);
         delayMicroseconds(200);
         // wait for response of 0b000000000
        // We will send two bytes from a 10-bit number
        // which is numChars * 5. The top three bits
        // of the 10-bit number comprise the first byte,
        // and the remaining 7 bits comprise the second
        // byte, although the byte needs to be shifted
        // left by one (not sure why)
        // the numbers are calculated above for timing reasons
        sendByteOnPin(byte1);
        delayMicroseconds(200);
        // wait for response of 0b000000000

        sendByteOnPin(byte2); // each char is worth 10
        delayMicroseconds(200);
        // wait for response of 0b000000000
        
        sendByteOnPin(0b100100001);
        // right now, the platten is moving, maybe?
        delayMicroseconds(1000); // not sure how long to wait
        // wait for response of 0b000000000
    } else if (numChars <= 25) {
        // not sure why this is so different
        sendByteOnPin(0b000001101);
        delayMicroseconds(200);
        // wait for response of 0b000000000

        sendByteOnPin(0b000000111);
        delayMicroseconds(200);
        // wait for response of 0b000000000

        sendByteOnPin(0b100100001); // each char is worth 10
        delayMicroseconds(200);
        // wait for response of 0b000000000
        
        sendByteOnPin(0b000000110);
        delayMicroseconds(200);
        // wait for response of 0b000000000

        sendByteOnPin(0b000000000);
        delayMicroseconds(200);
        // wait for response of 0b000000000

        sendByteOnPin(numChars * 10); // each char is worth 10
        delayMicroseconds(200);
        // wait for response of 0b000000000
        
        sendByteOnPin(0b100100001);
        // right now, the platten is moving, maybe?
        delayMicroseconds(1000); // not sure how long to wait
        // wait for response of 0b000000000
    }
    
    sendByteOnPin(0b000000101);
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    
    sendByteOnPin(0b010010000); // missing???
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    // 87ms wait!
    delay(87);
    
    sendByteOnPin(0b100100001);
    delayMicroseconds(200);
    // wait for response of 0b000000000
    
    
    sendByteOnPin(0b000001011);
    delayMicroseconds(200);
    // wait for final response of 0b001010000

    delay(2000); // wait for carriage

}

void sendBytes() {
    while (!q.isEmpty()) {
        sendByteOnPin(q.dequeue());
        // wait for low then high (for a zero)
        while (digitalRead(d2) == 1) {
          // busy
        }
        while (digitalRead(d2) == 0) {
          // busy
        }
    }
}


