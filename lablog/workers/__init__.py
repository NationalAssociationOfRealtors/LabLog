from celery import Celery
from celery import bootsteps
from kombu import Consumer
from lablog import config
from lablog import db
from lablog import messages
from lablog.models.client import Admin
from lablog.interfaces.wunderground import Wunderground
from lablog.interfaces.eagle import EnergyGateway
from lablog.interfaces.ups import UPS
from lablog.hooks import post_slack
import humongolus
import logging

MONGO = db.init_mongodb()
INFLUX = db.init_influxdb()
MQ = db.init_mq()
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL)
humongolus.settings(logging, MONGO)

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')

class PresenceConsumer(bootsteps.ConsumerStep):

    def handle_presence(self, body, msg):
        try:
            logging.info("Received Presence Message: {}".format(body))
            user = Admin(id=body['tags']['user_id'])
            user.in_office = body['fields']['value']
            user.save();
            disp = "arrived" if user.in_office else "departed"
            post_slack.delay(message={"text":"{} has {}".format(user.name, disp)})
        except Exception as e:
            logging.exception(e)
        finally:
            msg.ack()

    def get_consumers(self, channel):
        return [
            Consumer(
                channel,
                queues=[messages.Queues.presence],
                callbacks=[self.handle_presence],
                accept=['pickle']
            )
        ]

app.steps['consumer'].add(PresenceConsumer)

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
    ups.go(INFLUX, MQ, messages.Exchanges.energy)
    MQ.release()

@app.task
def get_weather_data():
    api_key = config.WUNDERGROUND_KEY
    station_id = config.WUNDERGROUND_STATION_ID
    w = Wunderground(api_key, station_id)
    w.go(INFLUX, MQ, messages.Exchanges.weather)
    MQ.release()

@app.task
def get_smartmeter_data():
    macid = config.SMART_METER_MACID
    un = config.SMART_METER_UN
    pw = config.SMART_METER_PW
    eg = EnergyGateway(macid, un, pw, "http://energy.entropealabs.mine.nu")
    eg.go(INFLUX, MQ, messages.Exchanges.energy)
    MQ.release()
