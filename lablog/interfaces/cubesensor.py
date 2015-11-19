from lablog.interfaces import Interface
import humongolus.field as field
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from lablog import messages, config
import requests
import logging
import os
from lablog import config
import json
from rauth import OAuth1Service, OAuth1Session

class CubeSensor(Interface):
    exchange = messages.Exchanges.node
    measurement_key = "cubesensor"
    run_delta = timedelta(seconds=30)
    consumer_key = config.CUBESENSOR_CONSUMER_KEY
    consumer_secret = config.CUBESENSOR_CONSUMER_SECRET
    access_token = config.CUBESENSOR_ACCESS_TOKEN
    access_token_secret = config.CUBESENSOR_ACCESS_TOKEN_SECRET

    KEYS = ['noisedba', 'noise','temp', 'pressure', 'humidity', 'voc', 'voc_resistance', 'battery', 'light', 'rssi', 'shake']

    def data(self, data=None):

        session = OAuth1Session(
        	consumer_key,
        	consumer_secret,
        	access_token,
        	access_token_secret)

        logging.info("Cube Sensors!")
        logging.info(session.get('%s/devices/' % RES).json())
        logging.info(session.get('%s/devices/%s/current' % (RES, device_id)).json())

        return session.get('%s/devices/%s/current' % (RES, device_id)).json()

    def point(self, value, namespace, field):
        t = datetime.utcnow()
        value = self.parse_value(value)
        return dict(
            measurement="{}.{}.{}".format(self.measurement_key, namespace, self.slugify(field)),
            time=t,
            tags=dict(
                station_id=self.mac_address,
                interface=str(self._id),
            ),
            fields=dict(
                value=value
            )
        )

    def parse_data(self, data):
        points = []
        t = datetime.utcnow()
        outdoor = data["body"]["devices"][0]["modules"][0]["dashboard_data"]
        indoor = data["body"]["devices"][0]["dashboard_data"]

        for k in self.KEYS:
            i = indoor.get(k)
            o = outdoor.get(k)
            if i: points.append(self.point(i, 'indoor', k))
            if o: points.append(self.point(o, 'outdoor', k))

        return points

    def slugify(self, value):
        return "{}".format(value.replace("_", "-")).lower()

    def parse_value(self, v):
            try:
                value = float(v)
            except:
                try:
                    value = float(v[0:-1])
                except:
                    value = 0
            return value
