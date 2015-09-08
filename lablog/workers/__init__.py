from snimpy.manager import Manager as M
from snimpy.manager import load
from celery import Celery
from lablog import config
from lablog import db
from lablog import messages
import humongolus
import logging
import requests
from datetime import datetime

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')
INFLUX = db.init_influxdb()
MQ = db.init_mq()

load("/app/data/mib/RFC1155-SMI.txt")
load("/app/data/mib/RFC-1215")
load("/app/data/mib/RFC-1212-MIB.txt")
load("/app/data/mib/RFC1213-MIB.txt")
load("/app/data/mib/stdupsv1.mib")
m = M(config.UPS_SMNP_IP, "NARpublic", 1)

@app.task
def monitor_ups():
    model = str(m.upsIdentModel).strip()
    manuf = str(m.upsIdentManufacturer).strip()
    points = []
    points.append(dict(
        measurement="ups_battery_voltage",
        tags=dict(
            model=model,
            manufacturer=manuf
        ),
        time=datetime.utcnow(),
        fields=dict(
            value=int(m.upsBatteryVoltage)
        )
    ))

    points.append(dict(
        measurement="ups_battery_current",
        tags=dict(
            model=model,
            manufacturer=manuf
        ),
        time=datetime.utcnow(),
        fields=dict(
            value=int(m.upsBatteryCurrent)
        )
    ))



    for l in m.upsInputFrequency:
        points.append(dict(
            measurement="ups_input_frequency",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=int(l),
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=int(m.upsInputFrequency[l])
            )
        ))

    for l in m.upsInputVoltage:
        points.append(dict(
            measurement="ups_input_voltage",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=int(l),
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=int(m.upsInputVoltage[l])
            )
        ))

    for l in m.upsOutputCurrent:
        points.append(dict(
            measurement="ups_output_current",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=int(l),
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=int(m.upsOutputCurrent[l])
            )
        ))

    for l in m.upsOutputPower:
        points.append(dict(
            measurement="ups_output_power",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=int(l),
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=int(m.upsOutputPower[l])
            )
        ))

    INFLUX.write_points(points)
    for i in points:
        messages.publish(MQ, i, messages.Exchanges.sensors, routing_key="ups.{}".format(i['measurement']))

@app.task
def get_weather_data():

    KEYS = ['UV', 'dewpoint_c', 'feelslike_c', 'heatindex_c', 'precip_1hr_metric',
        'precip_today_metric', 'pressure_in', 'pressure_mb', 'relative_humidity',
        'solarradiation', 'temp_c', 'visibility_km', 'wind_degrees', 'wind_gust_kph', 'wind_kph', 'windchill_c']

    def slugify(value):
        return "{}".format(value.replace("_", "-")).lower()

    api_key = config.WUNDERGROUND_KEY
    station_id = config.WUNDERGROUND_STATION_ID
    current_conditions = "http://api.wunderground.com/api/{}/conditions/q/pws:{}.json".format(api_key, station_id)
    res = requests.get(current_conditions)
    data = res.json()

    points = []
    for k,v in data.get('current_observation').iteritems():
        if k in KEYS:
            try:
                value = float(v)
            except:
                try:
                    value = float(v[0:-1])
                except:
                    value = 0

            points.append(dict(
                measurement=slugify(k),
                time=datetime.utcnow(),
                tags=dict(
                    station_id=station_id
                ),
                fields=dict(
                    value=value
                )
            ))

    INFLUX.write_points(points)
    for i in points:
        messages.publish(MQ, i, messages.Exchanges.sensors, routing_key="weather.{}".format(i['measurement']))
