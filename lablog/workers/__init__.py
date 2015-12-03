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
            for t in self.triggers:
                if t.key == body['measurement']:
                    val = t._run(body)
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
def run_interfaces():
    for loc in Location.find():
        try:
            logging.info("Monitoring Location: {}".format(loc.name))
            for i in loc.interfaces:
                logging.info("Running Interface: {}".format(i.interface.__class__.__name__))
                try:
                    i.interface.run(INFLUX, MQ)
                except Exception as e:
                    logging.error(e)
                logging.info("Finished Interface: {}".format(i.interface.__class__.__name__))
        except Exception as e:
            logging.error(e)
    MQ.release()
