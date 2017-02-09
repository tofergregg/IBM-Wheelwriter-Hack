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

void setup() 
{
  // initialize serial communication at 57600 bits per second:
  Serial.begin(57600);

  Serial.setTimeout(25);
  
  // Digital pins
  pinMode(d2, OUTPUT); // listening pin

  // test the output pin by starting it low
  //PORTD &= 0b11111011;
  PORTD &= 0b00000000; // turn all off
  PORTD |= 0b01000000; // turn on
  
}

// the loop routine runs over and over again forever:
void loop() 
{
      // set pin high
      //PORTD |= 0b00000100;
      Bean.sleep(100000);  
}



