#include <MQ135.h>
#include <DHT.h>

#define PIN_DHT 2
#define DHT_TYPE DHT22
#define PIN_MQ135 A1
#define DST_IP "192.168.1.176"
#define DST_PORT 4000

MQ135 mq135(PIN_MQ135);
DHT dht(PIN_DHT, DHT_TYPE);

bool connectedToWifi = false;

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200);

  Serial.println("Connecting to WiFi...");
  Serial1.println("AT+RST");
  delay(1000);  
    
  Serial1.println("AT+CWMODE=1");
  delay(1000);
    
  Serial1.println("AT+CWJAP=\"coffeshop\",\"coffe91shop\"");
  delay(1000);
  
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

  String data = String("{\"ppm\":") + ppm + 
                ",\"rzero\":" + rzero + 
                ",\"temperature\":" + temperature +
                ",\"humidity\":" + humidity + "}";

  Serial.println(data);

  if (connectedToWifi) {
    Serial1.println("AT+CIPMUX=0");
    delay(1000);
    Serial1.println("AT+CIPSTART=\"TCP\",\"pi\",4000");
    delay(1000);
    String postCommand = String("POST /stats HTTP/1.0\r\n") + 
                         "Host:pi\r\n" + 
                         "Content-Type: application/json\r\n" +
                         "Content-Length: " + data.length() + "\r\n" +
                         data;
    Serial1.print("AT+CIPSEND=");
    Serial1.println(postCommand.length());
    if (Serial1.find(">")) {
      Serial1.print(postCommand);
    } else {
       Serial.println("Connect timeout");
    }
    Serial1.println("AT+CIPCLOSE");
  }

  delay(5000);
}
