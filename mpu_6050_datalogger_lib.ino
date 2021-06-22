#include <Adafruit_MPU6050.h>

Adafruit_MPU6050 mpu;
bool reading_success;
sensors_event_t accel_event, gyro_event, temp_event;

void setup()
{
    Serial.begin(9600);
    mpu.begin();
    mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
    mpu.setGyroRange(MPU6050_RANGE_2000_DEG);
    Serial.println("start");
}

void loop()
{
    reading_success = mpu.getEvent(&accel_event, &gyro_event, &temp_event);
    if(reading_success) {
        Serial.print(accel_event.acceleration.x); Serial.print(",");
        Serial.print(accel_event.acceleration.y); Serial.print(",");
        Serial.print(accel_event.acceleration.z); Serial.print(",");
        Serial.print(gyro_event.gyro.roll * 180/M_PI); Serial.print(",");
        Serial.print(gyro_event.gyro.pitch * 180/M_PI); Serial.print(",");
        Serial.println(gyro_event.gyro.heading * 180/M_PI);
        delay(80);
    }
    else {
        Serial.println("Read unsuccessful");
    }
}
