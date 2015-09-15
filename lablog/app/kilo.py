from geventwebsocket import WebSocketApplication
from kombu import Queue
from lablog import config
from lablog import db
from lablog.util.jsontools import JavascriptEncoder
from lablog.models.client import Token, Admin
from lablog.hooks import post_slack
from lablog import messages
from uuid import uuid4
from datetime import datetime
import humongolus
import requests
import gevent
import logging
import urlparse
import json
import os

logging.basicConfig(level=config.LOG_LEVEL)
MONGO = db.init_mongodb()
humongolus.settings(logging, MONGO)

class SocketException(Exception):

    def json(self):
        return {
            'message':self.message
        }

def verify_message(client, scopes):
    args = urlparse.parse_qs(client.environ.get('QUERY_STRING'))
    logging.info(args)
    token = args.get('token')[0]
    logging.info(token)
    client_id = args.get('client_id')[0]
    t = Token.find_one({'access_token':token})
    if t and str(t._get('client')._value) == client_id and t.expires > datetime.utcnow():
        for i in scopes:
            if not i in t.scopes: raise SocketException('Invalid scope')
        return t
    else:
        raise SocketException("Invalid Token")

class Kilo(WebSocketApplication):

    def __init__(self, *args, **kwargs):
        super(Kilo, self).__init__(*args, **kwargs)

    @classmethod
    def protocol_name(cls):
        return "json"

    def node_stream(self, body, msg):
        current = self.ws.handler.active_client
        self.sendto({'event':'node', '_to':current.address, 'data':json.dumps(body, cls=JavascriptEncoder)})
        return True

    def on_open(self):
        try:
            token = verify_message(self.ws.handler.active_client.ws, ['inoffice', 'analytics'])
        except SocketException as e:
            logging.error(e)
            self.ws.handler.active_client.ws.send(json.dumps({'event':'invalid_access',  'data':e.json()}))
            return
        self.INFLUX = db.init_influxdb()
        self.MQ = db.init_mq()
        current = self.ws.handler.active_client
        current.token = token
        q = Queue(
            name="{}".format(current.address),
            exchange=messages.Exchanges.sensors,
            routing_key="node.*",
            exclusive=True,
        )
        consumer = messages.Consumer(self.MQ, [q], self.node_stream)
        self.greenlet = gevent.spawn(consumer.run)

    def on_message(self, message):
        if not message: return
        try:
            token = self.ws.handler.active_client.token
            ms = json.loads(message)
            ms['token'] = token
            ev = ms['event']
            ms['_to'] = tuple(ms.get('_to', {}))
            actions = {
                'inoffice': self.inoffice,
                'beacons': self.beacons,
                'ping': self.ping,
            }
            actions[ev](ms)
        except SocketException as e:
            logging.exception(e)
            self.ws.handler.active_client.ws.send(json.dumps({'event':'invalid_access',  'data':e.json()}))
        except Exception as e:
            logging.exception(e)

    def ping(self, data):
        logging.info(u"{} pinged...".format(data['token'].user.name))

    def beacons(self, data):
        #TODO write beacon data to data store
        #logging.info(data['data']['result']['beacons'])
        pass

    def inoffice(self, data):
        logging.info("In-Office: {}".format(data['data']['result']))
        user = data['token'].user
        user.in_office = data['data']['result']
        point = [dict(
            measurement="inoffice",
            tags=dict(
                user_id=str(user._id),
                client_id=str(data['token'].client._id)
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=data['data']['result']
            )
        )]
        self.INFLUX.write_points(point)
        user.save();
        u = user.json()
        u['times'] = user.get_punchcard(self.INFLUX)
        data['data']['user'] = u
        self.broadcast(data)
        disp = "arrived" if user.in_office else "departed"
        post_slack.delay(message={"text":"{} has {}".format(user.name, disp)})

    def on_close(self, reason):
        MONGO.close()
        self.MQ.release()
        gevent.kill(self.greenlet)
        current = self.ws.handler.active_client
        logging.info("Client Left: {}".format(current.address))

    def sendto(self, ms):
        _to = self.ws.handler.server.clients.get(ms['_to'])
        if _to: _to.ws.send(json.dumps(ms, cls=JavascriptEncoder))

    def broadcast(self, message):
        for client in self.ws.handler.server.clients.values():
            try:
                client.ws.send(json.dumps(message, cls=JavascriptEncoder))
            except Exception as e:
                logging.error(e)
