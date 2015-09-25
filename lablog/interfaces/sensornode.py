from lablog.interfaces import Interface
from lablog.util import aes
from lablog import config
from datetime import datetime
import json

k = list(config.SKEY)
k.append(0x00)
SKEY = bytearray(k)
KEY = buffer(SKEY)

class Node(Interface):

    def __init__(self, id):
        self.id = id

    def data(self, data=None):
        j = aes.decrypt(data, KEY)
        j = json.loads(j)
        return j

    def parse_data(self, data):
        points = []
        for k,v in data.iteritems():
            if v:
                points.append(dict(
                    measurement="node.{}".format(k),
                    tags=dict(
                        node=str(self.id),
                    ),
                    time=datetime.utcnow(),
                    fields=dict(
                        value=v,
                    )
                ))
        return points
