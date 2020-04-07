#include <MQ135.h>
#include <DHT.h>

#define PIN_DHT 2
#define DHT_TYPE DHT22
#define PIN_MQ135 A1

#define SSID      ""
#define SSID_PASS ""
#define DST_IP    ""
#define DST_PORT  80

MQ135 mq135(PIN_MQ135);
DHT dht(PIN_DHT, DHT_TYPE);

bool connectedToWifi = false;

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);

  Serial.println("Connecting to WiFi...");
  Serial1.println("AT+RST");    
  Serial1.println("AT+CWMODE=1");
  delay(1000);

  String connectCommand = "AT+CWJAP=";
  connectCommand += "\"";
  connectCommand += SSID;
  connectCommand += "\",\"";
  connectCommand += SSID_PASS;
  connectCommand += "\"";  
  Serial1.println(connectCommand);
  delay(2000);
  
  if (Serial1.find("OK")) {
    connectedToWifi = true;
    Serial.println("Connected to WiFi");
  } else {
    connectedToWifi = false;
    Serial.println("Cannot connect to WiFi");
  }

  dht.begin();
}

void loop() {
  float rzero = mq135.getRZero();
  float ppm = mq135.getPPM();

  if (isnan(rzero) || isnan(ppm)) {
    Serial.println(F("Failed to read from MQ135 sensor"));
    return;
  }

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println(F("Failed to read from DHT22 sensor"));
    return;
  }

  String data = "";
  data += "{\"ppm\":";
  data += ppm;
  data += ",\"rzero\":";
  data += rzero;
  data += ",\"temperature\":";
  data += temperature;
  data += ",\"humidity\":";
  data += humidity;
  data += "}"; 

  Serial.println(data);

  if (connectedToWifi) {
    String connectCommand = String("AT+CIPSTART=\"TCP\",") + "\"" + DST_IP + "\","  + DST_PORT;
    Serial1.println(connectCommand);
    delay(2000);
    String postCommand = "POST /stats HTTP/1.0\r\n";
    postCommand += "Host:pi\r\n"; 
    postCommand += "Content-Type:application/json\r\n";
    postCommand += "Content-Length:";
    postCommand += data.length();
    postCommand += "\r\n";
    postCommand += data;
    Serial1.print("AT+CIPSEND=");
    Serial1.println(postCommand.length());
    Serial1.println(postCommand);
    Serial1.println("AT+CIPCLOSE");
  }

  delay(5000);
}
