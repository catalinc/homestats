#!/usr/bin/env python3
import serial
import time
import json
import sys
from influxdb import InfluxDBClient
from datetime import datetime

ifhost = "127.0.0.1"
ifport = 8086
ifuser = "grafana"
ifpass = "redcatisgreen"
ifdb = "home"
measurement_name = "home_stats"


def air_quality_index(ppm):
    if ppm <= 350:
        return 1
    if ppm <= 600:
        return 2
    if ppm <= 1000:
        return 3
    if ppm <= 5000:
        return 4
    return 5


if __name__ == "__main__":
    ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=10)
    ser.flush()
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").rstrip()
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print("Parse error: %s for input: %s" % (str(e), line))
                    sys.exit(1)
                timestamp = datetime.utcnow()
                ppm = data["ppm"]
                aiq = air_quality_index(ppm)
                body = [
                    {
                        "measurement": measurement_name,
                        "time": timestamp,
                        "fields": {
                            "temperature": data["temperature"],
                            "humidity": data["humidity"],
                            "ppm": ppm,
                            "air_quality_index": aiq,
                            "pressure": data["pressure_mmhg"]
                        },
                    }
                ]
                ifclient.write_points(body)
            time.sleep(1)
    except KeyboardInterrupt:
        ifclient.close()
        ser.close()
