
#include <analogWrite.h>

class Motor {

  public:

    Motor( int IOPin , int MapScale ) ;                      // Constructor to identify motor pin and later to add in calibration scales from IP to OP
    Motor( int IOPin , int Thresh , int Bool ) ;
    void drive( double SensorReading ) ;      // Function to send an adjusted signal to power the feedback motors

  private:

    int Pin ;
    double lastReading ;
    int lastPower ;
    int Power ;
    int Scale ;
    int Threshold ;
    bool Analog ;
    

  
} ;


Motor::Motor( int IOPin , int MapScale ) {
  Analog = true ;
  Pin = IOPin ;
  lastReading = 0 ;
  Scale = MapScale ;
  pinMode(Pin, OUTPUT);
  
}

Motor::Motor( int IOPin , int Thresh , int Bool) {
  Analog = false ;
  Pin = IOPin ;
  Threshold = Thresh ;
  pinMode(Pin, OUTPUT);
  
}


void Motor::drive( double SensorReading ) {

  analogWrite( Pin , SensorReading ) ;
  
}
  


