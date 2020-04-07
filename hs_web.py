#!/usr/bin/env python3

from bottle import run, post, request
from influxdb import InfluxDBClient
from datetime import datetime

ifhost = "127.0.0.1"
ifport = 8086
ifuser = "grafana"
ifpass = "redcatisgreen"
ifdb = "home"
measurement_name = "home_stats_mobile"

ifclient = InfluxDBClient(ifhost, ifport, ifuser, ifpass, ifdb)


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


@post("/stats")
def save_stats():
    data = request.json
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
            },
        }
    ]
    ifclient.write_points(body)


run(host="0.0.0.0", port=4000)
