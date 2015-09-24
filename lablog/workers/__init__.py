from celery import Celery
from lablog import config
from lablog import db
from lablog import messages
from lablog.interfaces.wunderground import Wunderground
from lablog.interfaces.eagle import EnergyGateway
from lablog.interfaces.ups import UPS
import humongolus
import logging

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')
INFLUX = db.init_influxdb()
MQ = db.init_mq()

@app.task
def monitor_ups():
    mibs = [
        "/app/data/mib/RFC1155-SMI.txt",
        "/app/data/mib/RFC-1215",
        "/app/data/mib/RFC-1212-MIB.txt",
        "/app/data/mib/RFC1213-MIB.txt",
        "/app/data/mib/stdupsv1.mib"
    ]
    ups = UPS(mibs, config.UPS_SNMP_IP, "NARpublic", 1)
    ups.go(INFLUX, MQ, messages.Exchanges.sensors)
    MQ.release()

@app.task
def get_weather_data():
    api_key = config.WUNDERGROUND_KEY
    station_id = config.WUNDERGROUND_STATION_ID
    w = Wunderground(api_key, station_id)
    w.go(INFLUX, MQ, messages.Exchanges.sensors)
    MQ.release()

@app.task
def get_smartmeter_data():
    macid = config.SMART_METER_MACID
    un = config.SMART_METER_UN
    pw = config.SMART_METER_PW
    eg = EnergyGateway(macid, un, pw, "http://energy.entropealabs.mine.nu")
    eg.go(INFLUX, MQ, messages.Exchanges.sensors)
    MQ.release()
