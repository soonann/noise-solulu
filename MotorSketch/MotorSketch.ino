#include <Servo.h>

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
Servo myservo;
int serIn;
int dState = 0;

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
     while (Serial.available()){
        
        int val = Serial.parseInt();  //read Serial and parse as int, will return 0 when it receives nothing anymore     
        if (val == 0){
          break;
        }
        serIn = val;
        Serial.println(serIn);  //prints the character just read
     }
     
    //the serial buffer is over just go to the line (or pass your favorite stop char)               
    Serial.println();
    spin(serIn);
  }
  
  //slows down the visualization in the terminal
  delay(1000);
}

void spin(int degree){
  Serial.println(degree);
  if (dState == degree){
    return;
  }

  int diff = ((dState + degree) % 360);
  Serial.println(diff);
  
  if (degree > 0){
    myservo.write(180);
  }
  else {
    myservo.write(0);
  }
  delay(0.116667 * diff);
  myservo.write(90);
}
