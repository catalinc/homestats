# Homestats

A simple Raspberry Pi service to monitor temperature, humidity, barometric pressure, ambient ligth, UV index, CO2 and TVOC levels.

# Sensors

- [SparkFun Air Quality Sensor SGP30 (Qwiic)](https://www.sparkfun.com/products/16531)
- [SparkFun Temp/Atmospheric/Humidity/Barometric Pressure Sensor BME280 (Qwiic)](https://www.sparkfun.com/products/15440)
- [AdaFruit ALS+UV Sensor LTR390 (Qwiic)](https://learn.adafruit.com/adafruit-ltr390-uv-sensor?view=all)
- [SparkFun 20x4 SerLCD - RGB Backlight (Qwiic)](https://www.sparkfun.com/products/16398)

All sensors are connected using the [Qwiic Connect System](https://www.sparkfun.com/qwiic).

# Prerequisites

1. InfluxDB and Grafana
2. Python 3

# Installation

1. Install InfluxDB and Grafana. I recommend [Installing InfluxDB & Grafana on Raspberry Pi](https://simonhearne.com/2020/pi-influx-grafana/) guide.
2. Clone this repo.
3. Install Python packages required for sensors: `sudo pip3 install -r requirements.txt`. 
3. Edit `homestats.ini` and set InfluxDB access credentials for Grafana user. Beware that the password is stored in plain text, so is probably better ensure that this file is readable only by the service user (usually the `pi` user).
4. Install the `homestats` service: `sudo ./install_service.sh` script. 
5. Start the service: `sudo systemctl start homestats.service`.
6. Open Grafana and import `homestats_dashboard.json` dashboard to visualise sensor data.