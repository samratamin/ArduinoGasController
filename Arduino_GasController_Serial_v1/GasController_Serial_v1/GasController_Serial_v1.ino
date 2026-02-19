% Arduino code to run on an Arduino of your choice.
%   




#include "math.h"
#include "string.h"

bool verboseMode = true;
bool purging = false;

int currentGPIO = 1;

long stopFETTime = 0;

void setup() 
{
    ShutdownGPIO();

    Serial.begin(115200);
    delay(20);
  
    for (int j=0; j<25; j++)
    {
      pinMode(j,OUTPUT);
    
    }


}

void loop() 
{
    ListenToSerial();

  
    if(millis() > stopFETTime)
    {
        ShutdownGPIO();
    }
    
    delay(20);
    
    
}

void ShutdownGPIO()
{
   for (int j=1; j<25; j++)
   {
      digitalWrite(j,LOW);
    
   }

   purging = false;

    
}



int charToInt (char inputChar)
{
    int returnInteger = 0;
    
    if(inputChar == '1')
    {
        returnInteger = 1;
    }
    else if(inputChar == '2')
    {
        returnInteger = 2;
    }
    else if(inputChar == '3')
    {
        returnInteger = 3;
    }
    else if(inputChar == '4')
    {
        returnInteger = 4;
    }
    else if(inputChar == '5')
    {
        returnInteger = 5;
    }
    else if(inputChar == '6')
    {
        returnInteger = 6;
    }
    else if(inputChar == '7')
    {
        returnInteger = 7;
    }
    else if(inputChar == '8')
    {
        returnInteger = 8;
    }
    else if(inputChar == '9')
    {
        returnInteger = 9;
    }
    else if(inputChar == '0')
    {
        returnInteger = 0;
    }
    
    
    return returnInteger;
}

int GetIntegerFromSerial()
{
    Serial.flush();
    clearSerialBuffer();
    
    int returnNumber = 0;
    

    do 
    {
        
        
        while (Serial.available() > 2) 
        {
            
            int numberOfDigits = Serial.available()-2;
           // Serial.println(numberOfDigits);
            char Data[numberOfDigits+1];
            
            for(int j=0;j<numberOfDigits;j++)
            {
                char Data = Serial.read();
                //Serial.print(charToInt(Data));
                returnNumber = returnNumber + charToInt(Data)*(pow(10,numberOfDigits-(j+1)));
            }
        
            
            
        }
        

    } while(returnNumber < 1);    
        

    Serial.flush();
    clearSerialBuffer();
    
    return returnNumber;
    
}

String getSerialString()
{
    

    clearSerialBuffer();
    
    
   String content = "";
  char character;

  while(Serial.available()) 
  {
      character = Serial.read();
      content.concat(character);
  }

  if (content != "" && verboseMode == true) {
    Serial.println(content);
  }
    
    
    return content;
    
}




void clearSerialBuffer()
{
    for(int j=1;j<Serial.available() + 1;j++)
    { 
        Serial.read();
        
    }
    
}



void ListenToSerial()
{
  
    char message[25];
  // if we get a valid byte, read analog ins:
  
  while (Serial.available() > 0) 
  {
    
   // inByte = Serial.read();
   for (int j=0;j<24;j++)
   {
       message[j] = Serial.read();
   }
   

     // Serial.println((message[0]-'0')*100);
      
      if( message[0]=='c' && message[1]=='o' && message[2]=='n' && message[3]=='n')
      {
        
        
        delay(10);
        Serial.println("true");
        
      }
      
      
      
      
      else if(message[0]=='G' && message[1]=='P' && message[2]=='I' && message[3]=='O' && message[6]==':')  
      {
          //Control GPIO
          //  Pulse a GPIO with formatted message:  GPIO08:005 will pulse GPIO 8 for 5 seconds
          //  Toggle a GPIO with formatted message:  GPIO08:H will turn GPIO High
          //  Toggle a GPIO with formatted message:  GPIO08:L will turn GPIO Low
          
          
          
          int GPIOPin = 0;
          
          GPIOPin = charToInt(message[4])*10 + charToInt(message[5]);
          
          
          pinMode(GPIOPin, OUTPUT);
          
          if(message[7] == 'H' || message[7] == 'L' || message[7] == 'h' || message[7] == 'l')
          {
              if(message[7] == 'H' || message[7] == 'h')
              {
                  digitalWrite(GPIOPin, HIGH);
              }
              else
              {
                  digitalWrite(GPIOPin, LOW);
              }
          }
          else
          {
              long OnSeconds = charToInt(message[7])*100 + charToInt(message[8])*10  + charToInt(message[9]);
              
              //RGB.color(0, 255, 0);
              //Serial.println(GPIOPin);
              //Serial.println(OnSeconds*1000);
              if(purging == false)
              {
                //Serial.print(F("Actuating GPIO "));
                //Serial.print(GPIOPin);
                //Serial.print(F(" for "));
                //Serial.print(OnSeconds*1000);
                //Serial.println(F(" ms "));
                
                digitalWrite(GPIOPin, HIGH);
                currentGPIO = GPIOPin;
                stopFETTime = millis() + (OnSeconds*1000);
                purging = true;
              }
              
              //delay(OnSeconds*1000);
              //stopFETTime = millis() + (OnSeconds*1000);
              //digitalWrite(GPIOPin, LOW);
              //Serial.println("done");
              //RGB.color(0, 0, 0);
          }
            
          
          
          
          
         
      }
      
     
      else
      {
        Serial.println(F("Invalid Command..."));
        
      }
      
  }
  
  
  
} 
