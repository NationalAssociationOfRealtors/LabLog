from geventwebsocket import WebSocketApplication
from lablog import config
from lablog import db
from lablog.util.jsontools import JavascriptEncoder
from lablog.models.client import Token, Admin
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

class SocketException(Exception):

    def json(self):
        return {
            'message':self.message
        }

def verify_message(client, scopes):
    args = urlparse.parse_qs(client.environ.get('QUERY_STRING'))
    token = args.get('token')[0]
    client_id = args.get('client_id')[0]
    t = Token.find_one({'access_token':token})
    if str(t._get('client')._value) == client_id and t.expires > datetime.utcnow():
        for i in scopes:
            if not i in t.scopes: raise SocketException('Invalid scope')
        return t
    else:
        raise SocketException("Invalid Token")

class Kilo(WebSocketApplication):

    def __init__(self, *args, **kwargs):
        super(Kilo, self).__init__(*args, **kwargs)
        self.MONGO = db.init_mongodb()
        humongolus.settings(logging, self.MONGO)
        logging.info("KILO running")

    @classmethod
    def protocol_name(cls):
        return "json"

    def node_stream(self):
        self.running = True
        current = self.ws.handler.active_client
        while self.running:
            now = datetime.utcnow()
            cur = self.MONGO['lablog']['node_stream'].find({'time':{'$gt':now}}, tailable=True, await_data=True)
            cur.hint([('$natural', 1)])
            while cur.alive:
                try:
                    doc = cur.next()
                    self.sendto({'event':'node', '_to':current.address, 'data':json.dumps(doc, cls=JavascriptEncoder)})
                except StopIteration:
                    gevent.sleep(1)


    def on_open(self):
        token = verify_message(self.ws.handler.active_client.ws, ['inoffice', 'analytics'])
        self.name = 'foo'
        current = self.ws.handler.active_client
        current.token = token
        current.INFLUX = db.init_influxdb()
        ev = {'event':'me', '_to':current.address, 'data':{'room':self.name}}
        self.sendto(ev)
        ev['event'] = 'joined'
        self.broadcast(ev)
        gevent.spawn(self.node_stream)

    def on_message(self, ms):
        try:
            token = self.ws.handler.active_client.token
            ms = json.loads(ms)
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
        self.ws.handler.active_client.INFLUX.write_points(point)
        user.save();
        u = user.json()
        u['times'] = user.get_punchcard(self.ws.handler.active_client.INFLUX)
        data['data']['user'] = u
        self.broadcast(data)
        disp = "arrived" if user.in_office else "departed"
        res = requests.post(config.SLACK_WEBHOOK, data=json.dumps({"text":"{} has {}".format(user.name, disp)}))

    def on_close(self, reason):
        self.running = False
        current = self.ws.handler.active_client
        logging.info("Client Left: {}".format(current.address))
        ev = {'event':'bye', 'data':{'room':self.name}}
        self.broadcast(ev)

    def sendto(self, ms):
        _to = self.ws.handler.server.clients.get(ms['_to'])
        if _to: _to.ws.send(json.dumps(ms, cls=JavascriptEncoder))

    def broadcast(self, message):
        for client in self.ws.handler.server.clients.values():
            try:
                client.ws.send(json.dumps(message, cls=JavascriptEncoder))
            except Exception as e:
                logging.error(e)
