from lablog.interfaces import Interface
from lablog.util import aes
from lablog import config
from lablog import messages
from datetime import datetime
import logging
import json

class Presence(Interface):

    exchange = messages.Exchanges.presence

    def data(self, data=None):
        return data

    def parse_data(self, data):
        points = []
        points.append(dict(
            measurement="presence",
            tags=dict(
                user_id=str(data['token'].user._id),
                interface=str(self._id),
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=data['data']['result'],
            )
        ))
        return points
