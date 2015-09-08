from kombu import Exchange, Queue
from kombu.mixins  import ConsumerMixin
from kombu.pools import producers
from datetime import datetime
from lablog import db
import logging

class Exchanges(object):
    sensors = Exchange('sensors', type='topic')

class Queues(object):
    node = Queue('node', Exchanges.sensors, routing_key="node.*")
    ups = Queue('ups', Exchanges.sensors, routing_key="ups.*")
    weather = Queue('weather', Exchanges.sensors, routing_key="weather.*")
    energy = Queue('energy', Exchanges.sensors, routing_key="energy.*")

class RequeueException(Exception): pass
class RejectException(Exception): pass

class Consumer(ConsumerMixin):

    def __init__(self, connection, queues, on_message=None):
        self.connection = connection
        self.on_message = on_message
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(self.queues, accept=['json', 'pickle'], callbacks=[self.process_message])]

    def process_message(self, body, msg):
        try:
            if self.on_message: self.on_message(body, msg)
            msg.ack()
        except RequeueException as e:
            logging.error(e)
            msg.requeue()
        except RejectException as e:
            logging.error(e)
            msg.reject()
        except Exception as e:
            msg.ack()

def publish(connection, payload, exchange, routing_key):
    with producers[connection].acquire(block=True) as producer:
        logging.info("Publishing: {} to exchange {} with routing {}".format(payload, exchange, routing_key))
        producer.publish(
            payload,
             serializer='pickle',
             compression='bzip2',
             exchange=exchange,
             declare=[exchange],
             routing_key=routing_key
        )
