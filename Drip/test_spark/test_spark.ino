#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>

#define ESP8266_LED 5

void setup() 
{
  Serial.begin(9600);
  Serial.println("hello");
  pinMode(ESP8266_LED, OUTPUT);
}

void loop() 
{
  Serial.println("hello");
  digitalWrite(ESP8266_LED, HIGH); // LED off
  delay(500);
  digitalWrite(ESP8266_LED, LOW); // LED on
  delay(500);
}
