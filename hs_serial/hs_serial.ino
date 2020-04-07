#include <MQ135.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_BMP3XX.h>
#include <Adafruit_SHT31.h>

#define MQ135_PIN A0
#define BMP_SCK 13
#define BMP_MISO 12
#define BMP_MOSI 11
#define BMP_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)

MQ135 mq135 = MQ135(MQ135_PIN);
Adafruit_BMP3XX bmp = Adafruit_BMP3XX(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);
Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(1);
  
  if(!bmp.begin()) {
    Serial.println(F("Could not find BMP3XX sensor"));
    while(1) delay(1);
  }

 if (!sht31.begin(0x44)) {
    Serial.println(F("Could not find SHT31"));
    while (1) delay(1);
  }

  bmp.setTemperatureOversampling(BMP3_OVERSAMPLING_8X);
  bmp.setPressureOversampling(BMP3_OVERSAMPLING_4X);
  bmp.setIIRFilterCoeff(BMP3_IIR_FILTER_COEFF_3);
}

void loop() {
  float temperature = sht31.readTemperature();
  float humidity = sht31.readHumidity();
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println(F("Failed to read from SHT31 sensor"));
    return;
  }

  float pressure = bmp.readPressure();
  float altitude = bmp.readAltitude(SEALEVELPRESSURE_HPA);
  if (isnan(pressure) || isnan(altitude)) {
    Serial.println(F("Failed to read from BMP3XX sensor"));
    return;
  }
  float mmhg = pressure * 0.00750062;

  float rzero = mq135.getRZero();
  float ppm = mq135.getPPM();
  if (isnan(ppm) || isnan(rzero)) {
    Serial.println(F("Failed to read from MQ135 sensor"));
    return;
  }

  Serial.print(F("{\"temperature\":"));
  Serial.print(temperature);
  Serial.print(F(",\"humidity\":"));
  Serial.print(humidity);
  Serial.print(F(", \"ppm\":"));
  Serial.print(ppm);
  Serial.print(F(",\"rzero\":"));
  Serial.print(rzero);
  Serial.print(F(",\"pressure_mmhg\":"));
  Serial.print(mmhg);
  Serial.print(F(",\"altitude\":"));
  Serial.print(altitude);
  Serial.println(F("}"));

  delay(5000);
}
