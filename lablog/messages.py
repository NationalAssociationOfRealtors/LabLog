from kombu import Exchange, Queue
from kombu.mixins  import ConsumerMixin
from kombu.pools import producers
from datetime import datetime
from lablog import db
import logging

class Exchanges(object):
    node = Exchange('node', type='topic')
    energy = Exchange('energy', type='topic')
    weather = Exchange('weather', type='topic')
    presence = Exchange('presence', type='direct')
    tasks = Exchange('tasks', type='direct')
    everything = Exchange('everything', type='fanout')


class Queues(object):
    presence = Queue('presence', Exchanges.presence, routing_key='presence')
    tasks = Queue('tasks', Exchanges.tasks, routing_key='tasks')
    everything = Queue('everything', Exchanges.everything)


class RequeueException(Exception): pass
class RejectException(Exception): pass

class Consumer(ConsumerMixin):

    def __init__(self, connection, queues, on_message=None):
        self.connection = connection
        self.on_message = on_message
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(self.queues, accept=['pickle'], callbacks=[self.process_message])]

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
        logging.debug("Publishing: {} to exchange {} with routing {}".format(payload, exchange, routing_key))
        producer.publish(
            payload,
             serializer='pickle',
             compression='bzip2',
             exchange=exchange,
             declare=[exchange],
             routing_key=routing_key
        )
        producer.publish(
            payload,
            serializer='pickle',
            compression='bzip2',
            exchange=Exchanges.everything,
            declare=[Exchanges.everything],
        )
