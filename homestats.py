#!/usr/bin/env python3
import time
import json
import sys
from influxdb import InfluxDBClient
from datetime import datetime
import board
import busio
import adafruit_bmp3xx
import adafruit_sht31d

ifhost = "127.0.0.1"
ifport = 8086
ifuser = "grafana"
ifpass = "redcatisorange"
ifdb = "home"
measurement_name = "homestats"
read_interval = 60

if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)
    sht = adafruit_sht31d.SHT31D(i2c)
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
    ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)
    try:
        while True:
            timestamp = datetime.utcnow()
            temperature = sht.temperature
            humidity = sht.relative_humidity
            pressure_mmhg = bmp.pressure * 0.750062
            body = [
                {
                    "measurement": measurement_name,
                    "time": timestamp,
                    "fields": {
                        "temperature": temperature,
                        "humidity": humidity,
                        "pressure": pressure_mmhg
                    },
                }
            ]
            ifclient.write_points(body)
            time.sleep(read_interval)
    except KeyboardInterrupt:
        ifclient.close()
