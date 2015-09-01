from snimpy.manager import Manager as M
from snimpy.manager import load
from celery import Celery
from lablog import config
from lablog import db
import humongolus
import logging
from datetime import datetime

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')
INFLUX = db.init_influxdb()

load("/app/data/mib/RFC1155-SMI.txt")
load("/app/data/mib/RFC-1215")
load("/app/data/mib/RFC-1212-MIB.txt")
load("/app/data/mib/RFC1213-MIB.txt")
load("/app/data/mib/stdupsv1.mib")
m = M(config.UPS_SMNP_IP, "NARpublic", 1)

model = m.upsIdentModel
manuf = m.upsIdentManufacturer

@app.task
def monitor_ups():
    points = []
    points.append(dict(
        measurement="ups_battery_voltage",
        tags=dict(
            model=model,
            manufacturer=manuf
        ),
        time=datetime.utcnow(),
        fields=dict(
            value=m.upsBatteryVoltage
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
            value=m.upsBatteryCurrent
        )
    ))



    for l in m.upsInputFrequency:
        points.append(dict(
            measurement="ups_input_frequency",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=l,
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=m.upsInputFrequency[l]
            )
        ))

    for l in m.upsInputVoltage:
        points.append(dict(
            measurement="ups_input_voltage",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=l,
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=m.upsInputVoltage[l]
            )
        ))

    for l in m.upsOutputCurrent:
        points.append(dict(
            measurement="ups_output_current",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=l,
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=m.upsOutputCurrent[l]
            )
        ))

    for l in m.upsOutputPower:
        points.append(dict(
            measurement="ups_output_power",
            tags=dict(
                model=model,
                manufacturer=manuf,
                line=l,
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=m.upsOutputPower[l]
            )
        ))

    INFLUX.write_points(points)
