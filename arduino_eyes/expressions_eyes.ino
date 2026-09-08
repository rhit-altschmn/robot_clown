#include <Adafruit_NeoPixel.h>
// #include <ros.h>
// #include <std_msgs/Float64MultiArray.h>
// #include <std_msgs/String.h>


// ros::NodeHandle nh;

#define PIN 4              // Arduino pin 6 to DIN of 8x32 matrix.
#define LED_COUNT 256*2      // 8x32 = 256 NeoPixel leds
#define BRIGHTNESS 8       // to reduce current for 256 NeoPixels

Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_COUNT, PIN, NEO_GRB + NEO_KHZ800);
bool Manip = false;
char incomingChar;
// int i = 0;
// int j = 0;
unsigned long previousMillis = 0;
unsigned long previousMillis2 = 0;
const long interval = 5000;   //7500
const long interval2 = 9500;
int currentExpression;
// bool emote;
String emotion = "base";


// float vUFu = 0.277;
// float vBU = 0.139;
// float vDB = 0.001;
// float vFdD = -0.337;
// float upper_limit = 0.415;
// float lower_limit = -1.917;

// float horiz;
// float vert;

float eye_edges[6] = {-2.75,-1.96,-1.18,-0.4,	0.4,1.18};   //{1.178097245,	0.3926990817,	-0.3926990817,	-1.178097245,	-1.963495408,	-2.748893572}
// float pupil_vert_edges[4] = {-0.337,0.001,0.139,0.277};  //verticals

int sq_corner[8] = {0,64,64*2,64*3,64*4,64*5,64*6,64*7};
int eye_pos_index;
int pupil_loc;

String eye_loc_num;
String pupil_loc_num;

//eye emotions
int baseEyeNums[20] = {2,3,4,5,9,14,16,23,24,31,32,39,40,47,49,54,58,59,60,61};
int closedEyeNums[6] = {11,21,25,38,42,52};

int happyEyeNums[6] = {12,18,30,33,45,51};
int confusedLeftNums[15] = {4, 10, 12, 18, 29, 34, 45, 50, 61, 22, 25, 38, 41, 54, 57};
int confusedLeftPupil[2] = {36, 43};
int confusedRightNums[17] = {3, 5, 11, 26, 27, 28, 28, 33, 47, 49, 61, 60, 59, 58, 54, 40, 38};
int confusedRightPupil[2] = {43,44};

// pupils
int centerPupils[4] = {27,28,35,36};
int slightUpPupils[4] = {28,29,34,35};
int upPupils[4] = {29,30,33,34};
int slightDownPupils[4] = {26,27,36,37};
int downPupils[4] = {25,26,37,38};

int rightPupils[4] = {11,12,19,20};
int slightRightPupils[4] = {19,20,27,28};
int slightLeftPupils[4] = {35,36,43,44};
int leftPupils[4] = {43,44,51,52};

int upRightPupils[4] = {18,19,28,29};
int upLeftPupils[4] = {34,35,44,45};
int downRightPupils[4] = {20,21,26,27};
int downLeftPupils[4] = {36,37,42,43};


uint8_t eyeLineColor[3] = {0,0,255};
uint8_t eyePupilColor[3] = {0,250,150};



// void camOCb(const std_msgs::Float64MultiArray & state_msg){
//   horiz = state_msg.data[0];
//   vert = state_msg.data[1];
// }

// void cam1Cb(const std_msgs::String & state_msg){
//   incomingChar = state_msg.data[0];
// }

// ros::Subscriber<std_msgs::Float64MultiArray> sub("/head_camera_jointstate", camOCb);

// ros::Subscriber<std_msgs::String> sub_1("/keyboard_input", cam1Cb);

void setup() {
  strip.begin();
  strip.show();            // Initialize all pixels to 'off'
  strip.setBrightness(BRIGHTNESS);   // overall brightness
  Serial.begin(57600);
  happyEyes(0);
  delay(5000);
  baseEyes(0,0);
  currentExpression = 1;

  eye_pos_index = 0;
  pupil_loc = 0;
  // nh.initNode();
  // nh.subscribe(sub);
  // nh.subscribe(sub_1);
}


void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentMillis = millis();
  // eye_pos_index = camPanMap(horiz);
  // pupil_loc = camTiltMap(vert);

  if (emotion == "base"){
    baseEyes(eye_pos_index,pupil_loc);
    if(currentMillis - previousMillis >= interval){
      // save last time homie blinked
      previousMillis = currentMillis;
      
      closedEyes(eye_pos_index);
      delay(200); //150
      baseEyes(eye_pos_index,pupil_loc);
    }
  }
  
  else{
    
    // switch(emotion){
    //   case "happy":
    //     happyEyes(eye_pos_index);
    //     break;
    //   case "confused":
    //     confusedEyes(eye_pos_index);
    //     break;



    // }

    if (emotion == "happy"){
      happyEyes(eye_pos_index);
    }
    if (emotion == "confused"){
      confusedEyes(eye_pos_index);
    }

    if(currentMillis - previousMillis2 >= interval2){
      previousMillis2 = currentMillis; 
      emotion = "base";     
      
    }
  }

  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Read until newline
    Serial.print("You entered: ");
    Serial.println(input); //Eye:# Pup:##

    eye_loc_num = input.charAt(4);  //Eye:# Pup:##
    eye_pos_index = eye_loc_num.toInt();

    pupil_loc_num = input.substring(10);
    pupil_loc = pupil_loc_num.toInt();

    Serial.print("Processed Eye pos: ");
    Serial.print(eye_pos_index);
    Serial.print(" pupil loc: "); 
    Serial.println(pupil_loc);

  }

  // while (Serial.available()){
  //   char incomingChar = Serial.read();
  //   Serial.print("I received: ");
  //   Serial.println(incomingChar);

    // switch(incomingChar) {     
    //   case '2':
    //     emotion = "happy";
    //     Serial.println("set emotion happy");
    //     break;
    //   case '3':
    //     emotion = "sad";
    //     break;
    //   case '4':
    //     emotion = "confused";
    //     break;
    //   case '5':
    //     emotion = "angry";
    //     break;
    //   case '1':
    //     emotion = "base";
    //     Serial.println("set emotion base");
    //     break;      
    // }

  // }





  // nh.spinOnce();
  delay(100);

}



//------ Eyes  ------

void baseEyes(int eye_index, int pupils){
  strip.clear();

  for (int n = 0; n < 20; n++){
    strip.setPixelColor(sq_corner[eye_index] + baseEyeNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
    strip.setPixelColor(sq_corner[eye_index+1] + baseEyeNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
  }

  drawPupils(eye_index,pupils);
  strip.show();

}

void closedEyes(int eye_index){
  strip.clear();

  for (int n = 0; n < 6; n++){
    strip.setPixelColor(sq_corner[eye_index] + closedEyeNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
    strip.setPixelColor(sq_corner[eye_index+1] + closedEyeNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
  }
  strip.show();
}

void happyEyes(int eye_index){
  strip.clear();

  for (int n = 0; n < 6; n++){
    strip.setPixelColor(sq_corner[eye_index] + happyEyeNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
    strip.setPixelColor(sq_corner[eye_index+1] + happyEyeNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
  }
  strip.show();
}

void confusedEyes(int eye_index){
  strip.clear();

  for (int n = 0; n < 15; n++){
    strip.setPixelColor(sq_corner[eye_index] + confusedLeftNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
  }
  for (int n = 0; n < 17; n++){
    strip.setPixelColor(sq_corner[eye_index+1] + confusedRightNums[n], eyeLineColor[0],eyeLineColor[1],eyeLineColor[2]);
  }

  for (int m = 0; m < 2; m++){
    strip.setPixelColor(sq_corner[eye_index] + confusedLeftPupil[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
    strip.setPixelColor(sq_corner[eye_index+1] + confusedRightPupil[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
  }
  
  strip.show();
}


// --------- moving pupils ---------------------------------------------------
void drawPupils(int eye_index, int pupil_loc){
  //up1, ur2, su3, ul4, right5, sr6, center7, sl8, left9, dr10, sd11, dl12, down13
  if (pupil_loc == 0){
    for (int m = 0; m < 4; m++){
      strip.setPixelColor(sq_corner[eye_index] + upPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
      strip.setPixelColor(sq_corner[eye_index+1] + upPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
    }
  }

  if (pupil_loc == 1){
    for (int m = 0; m < 4; m++){
      strip.setPixelColor(sq_corner[eye_index] + slightUpPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
      strip.setPixelColor(sq_corner[eye_index+1] + slightUpPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
    }
  }

  if (pupil_loc == 2){
    for (int m = 0; m < 4; m++){
      strip.setPixelColor(sq_corner[eye_index] + centerPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
      strip.setPixelColor(sq_corner[eye_index+1] + centerPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
    }
  }

  if (pupil_loc == 3){
    for (int m = 0; m < 4; m++){
      strip.setPixelColor(sq_corner[eye_index] + slightDownPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
      strip.setPixelColor(sq_corner[eye_index+1] + slightDownPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
    }
  }

  if (pupil_loc == 4){
    for (int m = 0; m < 4; m++){
      strip.setPixelColor(sq_corner[eye_index] + downPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
      strip.setPixelColor(sq_corner[eye_index+1] + downPupils[m], eyePupilColor[0],eyePupilColor[1],eyePupilColor[2]);
    }
  }

}

