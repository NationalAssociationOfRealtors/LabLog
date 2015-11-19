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

class CubeSensor(Interface):
    exchange = messages.Exchanges.node
    measurement_key = "cubesensor"
    run_delta = timedelta(seconds=30)

    
    consumer_key = config.CUBESENSOR_CONSUMER_KEY
    consumer_secret = config.CUBESENSOR_CONSUMER_SECRET

    KEYS = ['noisedba', 'noise','temp', 'pressure', 'humidity', 'voc','voc_resistance','battery','light','rssi','shake']

    def data(self, data=None):
        authorization = lablog.util.lnetatmo.ClientAuth()
        devList = lablog.util.lnetatmo.DeviceList(authorization)
        payload = devList.getStationsData(device_id=self.mac_address)
        logging.debug(payload)
        return payload

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
