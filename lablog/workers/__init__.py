from celery import Celery
from celery import bootsteps
from kombu import Consumer
from lablog import config
from lablog import db
from lablog import messages
from lablog.models.client import Admin
from lablog.models.location import Location
from lablog.hooks import post_slack
from lablog.triggers import Trigger
import logging

INFLUX = db.init_influxdb()
MQ = db.init_mq()

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')

class TriggerConsumer(bootsteps.ConsumerStep):

    def __init__(self, *args, **kwargs):
        self.triggers = [a for a in Trigger.find()]
        super(TriggerConsumer, self).__init__(*args, **kwargs)

    def handle_trigger(self, body, msg):
        try:
            logging.info("Received Trigger Message: {}".format(body))
            logging.info("Checking for qualified triggers")
            for t in self.triggers:
                if t.key == body['measurement']:
                    logging.info("Found trigger.")
                    val = t._run(body)
                    logging.info("Trigger Result: {}".format(val))
        except Exception as e:
            logging.exception(e)
        finally:
            msg.ack()

    def get_consumers(self, channel):
        return [
            Consumer(
                channel,
                queues=[messages.Queues.everything],
                callbacks=[self.handle_trigger],
                accept=['pickle']
            )
        ]

app.steps['consumer'].add(TriggerConsumer)

@app.task
def monitor_locations_30sec():
    clss = ['UPS', 'HomeEnergyMonitor', 'EnergyGateway']
    for loc in Location.find():
        for i in loc.interfaces:
            if i.interface.__class__.__name__  in clss:
                logging.info("Running Interface: {}".format(i.interface.__class__.__name__))
                try:
                    i.interface.go(INFLUX, MQ)
                except Exception as e:
                    logging.exception(e)
                logging.info("Finished Interface: {}".format(i.interface.__class__.__name__))
    MQ.release()

@app.task
def monitor_locations_5min():
    clss = ['Wunderground',]
    for loc in Location.find():
        for i in loc.interfaces:
            if i.interface.__class__.__name__  in clss:
                logging.info("Running Interface: {}".format(i.interface.__class__.__name__))
                i.interface.go(INFLUX, MQ)
                logging.info("Finished Interface: {}".format(i.interface.__class__.__name__))
    MQ.release()
