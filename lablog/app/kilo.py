from geventwebsocket import WebSocketApplication
from lablog import config
from lablog import db
from lablog.util.jsontools import JavascriptEncoder
from lablog.models.client import Token
from uuid import uuid4
from datetime import datetime
import humongolus
import gevent
import logging
import json

logging.basicConfig(level=config.LOG_LEVEL)

class SocketException(Exception):

    def json(self):
        return {
            'message':self.message
        }

def verify_message(message, scopes):
    ms = json.loads(message)
    token = ms['data']['auth']['token']
    client_id = ms['data']['auth']['client_id']
    t = Token.find_one({'refresh_token':token})
    if str(t._get('client')._value) == client_id and t.expires > datetime.utcnow():
        for i in scopes:
            if not i in t.scopes: raise SocketException('Invalid scope')
        ms['data']['user'] = t.user.json()
        ms['data']['user'].pop('password')
        return ms
    else:
        raise SocketException("Invalid Token")

class Kilo(WebSocketApplication):

    def __init__(self, *args, **kwargs):
        super(Kilo, self).__init__(*args, **kwargs)
        MONGO = db.init_mongodb()
        humongolus.settings(logging, MONGO)

    @classmethod
    def protocol_name(cls):
        return "json"

    def on_open(self):
        self.name = 'foo'
        current = self.ws.handler.active_client
        ev = {'event':'me', '_to':current.address, 'data':{'room':self.name}}
        self.sendto(ev)
        ev['event'] = 'joined'
        self.broadcast(ev)

    def on_message(self, ms):
        try:
            ms = verify_message(ms, ['inoffice'])
            logging.info(ms)
            ev = ms['event']
            ms['_to'] = tuple(ms.get('_to', {}))
            actions = {
                'inoffice': self.inoffice,
            }
            actions[ev](ms)
        except SocketException as e:
            logging.exception(e)
            logging.info(self.ws.handler.active_client)
            self.ws.handler.active_client.ws.send(json.dumps({'event':'invalid_access',  'data':e.json()}))
        except Exception as e:
            logging.exception(e)

    def inoffice(self, data):
        #TODO write beacon data to data store
        self.broadcast(data)

    def on_close(self, reason):
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
