#include <Wire.h>
#include "I2Cdev.h"
#include <MPU6050.h>

#define I2C_SDA 21
#define I2C_SCL 22
#define RESET 23
#define TRIGGER 32
#define THUMBSTICKX 39
#define THUMBSTICKY 36
#define THUMBSTICKSW 34

MPU6050 mpu;
int16_t ax, ay, az, gx, gy, gz;
uint8_t vx, vy;
uint16_t tsx, tsy; //ts - thumbstick
uint8_t tsb, fire;


void setup() {
  Serial.begin(115200);
  pinMode(RESET, INPUT_PULLUP);
  pinMode(THUMBSTICKX, INPUT);
  pinMode(THUMBSTICKY, INPUT);
  pinMode(THUMBSTICKSW, INPUT);
  pinMode(TRIGGER, INPUT_PULLUP);
  Wire.begin(I2C_SDA,I2C_SCL);
  mpu.initialize();
  if (!mpu.testConnection()) {
    while (1);
  }
}

void loop() {  
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    if (digitalRead(RESET) == HIGH) {
      vx = (gy+300)/200;
      vy = -(gz-100)/200;
    }
    else vx = vy = 0;
    tsx = analogRead(THUMBSTICKX);
    tsy = analogRead(THUMBSTICKY);
    tsb = digitalRead(THUMBSTICKSW) != 0 ? 1 : 0;

    fire = digitalRead(TRIGGER) != 0 ? 1 : 0;

    //sync signal
    Serial.write(0xFFFF);
    Serial.write(0xFFFF);
    //fire trigger
    Serial.write(fire);
    //thumbstick switch
    Serial.write(tsb);
    //thumbstick X
    Serial.write((uint8_t)(tsx >> 8));
    Serial.write((uint8_t)(tsx & 0x00FF));
    //thumbstick Y
    Serial.write((uint8_t)(tsy >> 8));
    Serial.write((uint8_t)(tsy & 0x00FF));
    //mouse movement
    Serial.write(vx);
    Serial.write(vy);
}
