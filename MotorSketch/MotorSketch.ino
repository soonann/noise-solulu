#include <Servo.h>

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
Servo myservo;
int serIn;

void setup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
  myservo.attach(A6);
  myservo.write(90);
}

void loop () {
  //simple feedback from Arduino  Serial.println("Hello World"); 
  
  // only if there are bytes in the serial buffer execute the following code
  if(Serial.available()) {    
    //inform that Arduino heard you saying something
    Serial.print("Arduino heard you say: ");
    
    //keep reading and printing from serial untill there are bytes in the serial buffer
     while (Serial.available() > 0){
        serIn = Serial.read();  //read Serial        
        Serial.print(serIn);  //prints the character just read
     }
     
    //the serial buffer is over just go to the line (or pass your favorite stop char)               
    Serial.println();
    spin();
  }
  
  //slows down the visualization in the terminal
  delay(1000);
}

void spin(){
  myservo.write(45); // rotate the motor counter-clockwise
  delay(5000); // keep rotating for 5 seconds (5000 milliseconds)

  myservo.write(90); // stop the motor
}
