#include <Servo.h>

String inputString = ""; // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete
Servo myservo;
int serIn;
double TIME_PER_DEGREE = 380 / 180.0; // to calculate how long it will take for 1 degree of rotation
int currDeg = 0;

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

void spin(int deg){

  // if the degree is already what we want, exit
  if (deg == currDeg) {
    return;
  }

  // otherwise calculate how long it will need to turn from curr state to desired state

  double duration = TIME_PER_DEGREE;
  deg = deg % 360;
  Serial.println(deg);

  // check which direction to turn
  if (currDeg > deg){
    duration = (duration * (currDeg - deg));
    myservo.write(180); // anti-clockwise
    delay(duration);
  } else {
    duration = (duration * (deg - currDeg));
    myservo.write(0); // clockwise
    delay(duration);
  }
  
  myservo.write(90); // stop turning
  currDeg = deg;
}
