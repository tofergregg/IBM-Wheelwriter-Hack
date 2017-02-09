/*
  Serial Test
 */

 // this holds all serial input until a full command is in it
String cmdBuffer;

// for the blink command
bool doBlink = false;
bool blinkState = true;
int blinkCnt = 0;
LedReading oldLed;


// the setup routine runs once
void setup()
{
  // initialize serial communication at 57600 bits per second:
  Serial.begin(57600);

  // on readBytes, return after 25ms or when the buffer is full
  Serial.setTimeout(25);
}


// the loop routine runs over and over again forever:
void loop()
{
  // this is the short-term buffer that gets added to the cmdBuffer
  char buffer[64];
  size_t length = 64; 

  // read as much as is available
  length = Serial.readBytes( buffer, length-1 );

  // null-terminate the data so it acts like a string
  buffer[length] = 0;

  // if we have data, so do something with it
  if ( length > 0 )
  {
      //Bean.setLed(255,0,0);
      Serial.print(buffer);
      //delay(100);
      //Bean.setLed(0,0,0);
  }

  Bean.sleep(50);
}

