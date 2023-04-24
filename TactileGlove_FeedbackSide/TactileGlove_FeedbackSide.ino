#include <WiFiClient.h>
#include <HTTPClient.h>
#include <analogWrite.h>
#include "motorClass.h"

// Define the network to connect to
const char* ssid = "TactileGlove" ;
const char* password = "012345678" ;

// Define URL to pressure path
const char* pressureURL = "http://192.168.4.1/grip" ;

#define TABLE_SIZE 256
byte lookup[TABLE_SIZE] {
  0, 0, 0, 0, 1, 1, 1, 2, 2, 3, 4, 5, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 18, 20, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 42, 44, 46, 49, 51, 54, 56, 59, 62, 64, 67, 70, 73, 76, 78, 81, 84, 87, 90, 93, 96, 99, 102, 105, 108, 111, 115, 118, 121, 124, 127, 130, 133, 136, 139, 143, 146, 149, 152, 155, 158, 161, 164, 167, 170, 173, 176, 178, 181, 184, 187, 190, 192, 195, 198, 200, 203, 205, 208, 210, 212, 215, 217, 219, 221, 223, 225, 227, 229, 231, 233, 234, 236, 238, 239, 240, 242, 243, 244, 245, 247, 248, 249, 249, 250, 251, 252, 252, 253, 253, 253, 254, 254, 254, 254, 254, 254, 254, 253, 253, 253, 252, 252, 251, 250, 249, 249, 248, 247, 245, 244, 243, 242, 240, 239, 238, 236, 234, 233, 231, 229, 227, 225, 223, 221, 219, 217, 215, 212, 210, 208, 205, 203, 200, 198, 195, 192, 190, 187, 184, 181, 178, 176, 173, 170, 167, 164, 161, 158, 155, 152, 149, 146, 143, 139, 136, 133, 130, 127, 124, 121, 118, 115, 111, 108, 105, 102, 99, 96, 93, 90, 87, 84, 81, 78, 76, 73, 70, 67, 64, 62, 59, 56, 54, 51, 49, 46, 44, 42, 39, 37, 35, 33, 31, 29, 27, 25, 23, 21, 20, 18, 16, 15, 14, 12, 11, 10, 9, 7, 6, 5, 5, 4, 3, 2, 2, 1, 1, 1, 0, 0, 0
};

// Timing variables
unsigned long lastMillis = 0 ;
const int interval = 5 ;
const int timeout = 20 ;
int attempts = 0 ;

// Storage variables
String pressure ;
int* pressureValues ;

// Global Threshold pressure values
int contactThreshold = 20 ;
int lowThreshold = 500 ;
int medThreshold = 1000 ;
int highThreshold = 1750 ;
int maxThreshold = 2500 ;

// Flags for use
bool contactFlag = false ;
bool lowFlag = false ;
bool medFlag = false ;
bool highFlag = false ;
bool maxFlag = false ;

// Frequencies for each threshold
int contactFreq ;
int lowFreq = 1 ;
int medFreq = 2 ;
int highFreq = 4 ;
int maxFreq = 8 ;

// Motor pin definitions and class constructions
#define Digit0 25
#define Digit1 23
#define Digit2 22
#define Digit3 21
#define Digit4 19

//Motor Thumb( Digit0 , 50 ) ;
//Motor Index( Digit1 , 60 ) ;
//Motor Middle( Digit2 , 40 ) ;
//Motor Ring( Digit3 , 40 ) ;
//Motor Pinky( Digit4 , 40 ) ;

Motor Thumb( Digit0 , 10 , 1 ) ;
Motor Index( Digit1 , 1 , 1 ) ;
Motor Middle( Digit2 , 10 , 1 ) ;
Motor Ring( Digit3 , 10 , 1 ) ;
Motor Pinky( Digit4 , 10 , 1 ) ;


// DEBUG STUFF
// #include "soc/soc.h"   // Drownout Detector stuff
// #include "soc/rtc_cntl_reg.h"
int i = 0 ;
int j = 0 ;

void setup() {

  //  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detection
  // Begin Serial connection for debugging
  Serial.begin(115200) ;
  Serial.setDebugOutput(true);

  connectWiFi() ;

  delay(1000);

}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentMillis = millis() ;

  if ( WiFi.status() == WL_CONNECTED ) { // Check still connected to WiFi
    if ( currentMillis - lastMillis >= interval ) { // Check timing interval
      pressure = RequestFrom( pressureURL ) ; // Get pressures from server
      // Serial.println(pressure) ;
      pressureValues = extractFrom( pressure ) ; // Convert string into double array for mathematical transforms
      lastMillis = millis() ; // Update timer
      // Logic to handle what signal to produce goes here.
      handle_input( pressureValues ) ;
    }

  } else {
    Serial.println("Connection lost. Attempting to reconnect.") ;
    connectWiFi() ;
  }

}


String RequestFrom(const char* serverName) {
  HTTPClient http;
  WiFiClient wifi ;

  // Your IP address with path or Domain name with URL path
  http.begin(wifi, serverName);
  http.setReuse( true ) ;

  // Send HTTP POST request

  int httpResponseCode = http.GET();


  String payload = "--";

  if (httpResponseCode > 0) {
    // Serial.print("HTTP Response code: ");
    // Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  // Free resources
  http.end();

  return payload;
}

int* extractFrom(String str) {

  char strr[25];
  str.toCharArray(strr, 25);
  char* pch;
  static int pcha[5];
  int i = 0;
  pch = strtok (strr, ","); // Define delimiters
  while (pch != NULL)
  {
    pcha[i] = atof(pch);   // Split and store
    pch = strtok (NULL, ",");
    i++ ;
  }

  return pcha;
}

void driveMotors( double SensorReading) {

//  Thumb.drive( SensorReading ) ;
  Index.drive( SensorReading ) ;
  Middle.drive( SensorReading ) ;
  Ring.drive( SensorReading ) ;
//  Pinky.drive( SensorReading ) ;

}

void connectWiFi() {

  attempts = 0 ;
  // Begin connection to WiFi
  WiFi.begin( ssid , password ) ;
  Serial.print("Connecting to WiFi") ;

  // Wait for connection and check for timeout
  while ( ( WiFi.status() != WL_CONNECTED ) && ( attempts < timeout ) ) {
    delay( 250 ) ;
    Serial.print(".") ;
    attempts++ ;
  }

  // Print success or failure
  if ( attempts >= timeout ) {
    Serial.println("\n Failed to connect. Request timed out.") ;
  } else {
    Serial.print("\nConnected to WiFi network with IP: ") ;
    Serial.println(WiFi.localIP()) ;
  }
}

void play_sine( int Freq ) {
  unsigned long start_time = millis() ;
  for (int i = 0 ; i < Freq ; i++) {
    unsigned long start_time = millis() ;
    for (int j = 0 ; j < TABLE_SIZE ; j = j + Freq ) {
      driveMotors(lookup[j]) ;
      delay(2) ;
    }
  }
  unsigned long end_time = millis() ;
  i = 0 ;
  driveMotors(0) ;

}

void play_chirp( String dir ) {
  if (dir == "close") {
    for (int j = 0 ; j < TABLE_SIZE/2 ; j++ ) {
      driveMotors(lookup[j]) ;
      delay(1) ;
    }
  } else if (dir == "open") {
    for (int j = 127 ; j < TABLE_SIZE ; j++ ) {
      driveMotors(lookup[j]) ;
      delay(1) ;
    }
  }
  driveMotors(0) ;
}

void handle_input(int* pressureValues) {

  int len = (sizeof(pressureValues)) - 1;// / sizeof(pressureValues[0])) ; // THIS SHOULDN'T WORK LOOK HERE IF STUFF GETS FUCKY.
  int averagePressure = 0 ;

  for ( int finger = 0 ; finger < len ; finger++ ) { // LIKEWISE THIS IS WORKAROUNDS
    Serial.println(String(finger) + " - " + String(pressureValues[finger])) ;
    // Average values of all fingers together 
    averagePressure += pressureValues[finger] ;
  }
  averagePressure = averagePressure / ( len ) ;
  // Serial.println("Average pressure: " + String(averagePressure)) ;
  // Checks against thresholds and flags to determine what signal to produce on the rising side
  if (( averagePressure > maxThreshold ) && !maxFlag && highFlag ) { // High to Max
    maxFlag = true ;
    Serial.println("High to Max") ;
    play_sine( maxFreq ) ;
  }
  else if (( averagePressure > highThreshold ) && !highFlag && medFlag ) { // Med to High
    highFlag = true ;
    Serial.println("Med to High") ;
    play_sine( highFreq ) ;
  }
  else if (( averagePressure > medThreshold ) && !medFlag && lowFlag ) { // Low to Med
    medFlag = true ;
    Serial.println("Low to Med") ;
    play_sine( medFreq ) ;
  }
  else if (( averagePressure > lowThreshold ) && !lowFlag && contactFlag ) { // Contact to Low
    lowFlag = true ;
    Serial.println("Contact to Low") ;
    play_sine( lowFreq ) ;
  }
  else if ((averagePressure > contactThreshold ) && !contactFlag ) { // Contact
    contactFlag = true ;
    Serial.println("Contact made") ;
    play_chirp( "close" ) ;
  }
  else if (( averagePressure < maxThreshold ) && maxFlag && highFlag ) { // Max to High
    maxFlag = false ;
    Serial.println("Max to High") ;
    play_sine( highFreq ) ;
  }
  else if (( averagePressure < highThreshold ) && highFlag && medFlag ) { // High to Med
    highFlag = false ;
    Serial.println("High to Med") ;
    play_sine( medFreq ) ;
  }
  else if (( averagePressure < medThreshold ) && medFlag && lowFlag ) { // Med to Low
    medFlag = false ;
    Serial.println("Med to Low") ;
    play_sine( lowFreq ) ;
  }
  else if (( averagePressure < lowThreshold ) && lowFlag && contactFlag ) { // Low to Contact
    lowFlag = false ;
    Serial.println("Low to Contact") ;
    play_chirp( "close" ) ;
  }
  else if ((averagePressure < contactThreshold ) && contactFlag ) { // Release
    contactFlag = false ;
    Serial.println("Release") ;
    play_chirp( "open" ) ;
  }


}
