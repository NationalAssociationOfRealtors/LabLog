from lablog.interfaces import Interface
import humongolus.field as field
from lablog.util import aes
from lablog import config
from lablog import messages
from datetime import datetime
import json
import logging

k = list(config.SKEY)
k.append(0x00)
SKEY = bytearray(k)
KEY = buffer(SKEY)

class Node(Interface):
    measurement_key = "node"
    exchange = messages.Exchanges.node

    id = field.Char()

    def data(self, data=None):
        j = aes.decrypt(data, KEY)
        j = json.loads(j)
        logging.info(j)
        return j

    def parse_data(self, data):
        v_map = {'t':'temperature','h':'humidity','l':'light','c':'co2','v':'voc','d':'dust','f':'fuel'}
        points = []
        for k,v in data.iteritems():
            k = v_map.get(k, k)
            if v:
                points.append(dict(
                    measurement="{}.{}".format(self.measurement_key, k),
                    tags=dict(
                        node=str(self.id),
                        interface=str(self._id),
                    ),
                    time=datetime.utcnow(),
                    fields=dict(
                        value=v,
                    )
                ))
        return points
