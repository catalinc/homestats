#!/usr/bin/env python3
import sys
import time
import configparser
import adafruit_sgp30
import adafruit_ltr390
import qwiic_bme280
import qwiic_serlcd
from influxdb import InfluxDBClient
from datetime import datetime
import board
import busio
from collections import OrderedDict
from typing import Tuple

# The key represents the CO2 interval (min, max) in ppm. 
# The value represents the color to use for display background.
CO2_LEVEL_COLOR = OrderedDict({
    # Normal background concentration in outdoor ambient air.
    (0, 400): (52, 235, 155),
    # Concentrations typical of occupied indoor spaces with good air exchange.
    (401, 1000): (137, 235, 52),
    # Complaints of drowsiness and poor air.
    (1001, 2000): (235, 205, 52),
    # Headaches, sleepiness and stagnant, stale, stuffy air.
    # Poor concentration, loss of attention, increased heart rate and slight nausea may also be present.
    (2001, 5000): (235, 110, 52),
    # Open a window and get the fuck out of the room.
    (5001, sys.maxsize): (255, 0, 0),
})

def get_lcd_background_color(co2: int) -> Tuple[int, int, int]:
    for k, v in CO2_LEVEL_COLOR.items():
        min_val = k[0]
        max_val = k[1]
        if min_val <= co2 <= max_val:
            return v
    return (255, 255, 255) # White

if __name__ == "__main__":

    config_file = "homestats.ini"
    if len(sys.argv) == 2:
        config_file = sys.argv[1]

    def fatal(s: str) -> None:
        print("ERROR: %s" % s)
        sys.exit(1)

    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    try:
        sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    except RuntimeError:
        fatal("The Qwiic SGP30 device isn't connected to the system")

    bme280 = qwiic_bme280.QwiicBme280()
    if not bme280.is_connected():
        fatal("The Qwiic BME280 device isn't connected to the system")
    if not bme280.begin():
        fatal("Cannot initialize Qwiic BME280 device")

    try:
        ltr = adafruit_ltr390.LTR390(i2c)
    except RuntimeError:
        fatal("The Qwiic LTR390 device isn't connected to the system")    

    lcd = qwiic_serlcd.QwiicSerlcd()
    if not lcd.connected:
        fatal("The Qwiic Serial LCD display isn't connected to the system")
    lcd.setContrast(5)
    lcd.begin()
    lcd.leftToRight()
    lcd.noCursor()
    lcd.display()

    config = configparser.ConfigParser()
    config.read(config_file)

    stats = config["measurement"]
    stats_name = stats["name"]
    stats_interval = stats.getint("interval")

    influx = config["influx"]
    ifhost = influx["host"]
    ifport = influx.getint("port")
    ifpass = influx["password"]
    ifuser = influx["username"]
    ifdb = influx["database"]
    ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)

    iaq_baseline = config["iaq_baseline"]
    eco2 = iaq_baseline.getint("eco2")
    tvoc = iaq_baseline.getint("tvoc")
    sgp30.iaq_init()
    sgp30.set_iaq_baseline(eco2, tvoc)

    try:
        while True:
            timestamp = datetime.utcnow()
            temperature_celsius = bme280.temperature_celsius
            humidity = round(bme280.humidity, 1)
            pressure_hpa = round(bme280.pressure / 100, 1)
            eco2 = sgp30.eCO2
            tvoc = sgp30.TVOC
            light = ltr.light
            uv = ltr.uvs

            body = [
                {
                    "measurement": stats_name,
                    "time": timestamp,
                    "fields": {
                        "temperature_celsius": temperature_celsius,
                        "humidity": humidity,
                        "pressure_hpa": pressure_hpa,
                        "eCO2": eco2,
                        "TVOC": tvoc,
                        "light": light,
                        "uv": uv
                    },
                }
            ]
            ifclient.write_points(body)

            lcd.clearScreen()
            bg_color = get_lcd_background_color(eco2)
            lcd.setFastBacklight(*bg_color)
            lcd.setCursor(0, 0)
            lcd.print(f"T:{temperature_celsius}C RH:{humidity}%")
            lcd.setCursor(0, 1)
            lcd.print(f"P:{pressure_hpa}hPa")
            lcd.setCursor(0, 2)
            lcd.print(f"CO2:{eco2}ppm L:{light}lx")
            lcd.setCursor(0, 3)
            lcd.print(f"TVOC:{tvoc}ppb UV:{uv}")

            time.sleep(stats_interval)
    except KeyboardInterrupt:
        ifclient.close()
