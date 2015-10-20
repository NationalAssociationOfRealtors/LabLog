from lablog.interfaces import Interface
import humongolus.field as field
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
from lablog import messages
import lablog.util.lnetatmo
import requests
import logging
import os
from lablog import config
import json

class NetAtmo(Interface):
    exchange = messages.Exchanges.node
    measurement_key = "netatmo"
    run_delta = timedelta(seconds=10)

    mac_address = field.Char()

    KEYS = ['Noise', 'Temperature', 'temp_trend', 'Humidity', 'Pressure','CO2']
    def data(self, data=None):

        authorization = lablog.util.lnetatmo.ClientAuth()

        devList = lablog.util.lnetatmo.DeviceList(authorization)
        payload = devList.getStationsData(device_id=self.mac_address)
        return payload

    def parse_data(self, data):
        points = []
        t = datetime.utcnow()
        #logging.info("=========all json===========")
        #logging.info(json.dumps(data["body"]["devices"], indent=4))
        #logging.info("=========alarms===========")
        #logging.info(data["body"]["devices"][0]["meteo_alarms"])
        #logging.info("=========outdoor module==========")
        #logging.info(data["body"]["devices"][0]["modules"][0]["dashboard_data"])

        for k,v in data["body"]["devices"][0]["modules"][0]["dashboard_data"].iteritems():
            if k in self.KEYS:
                logging.info(k)
                value = self.parse_value(v)
                points.append(dict(
                    measurement="{}.outdoor.{}".format(self.measurement_key, self.slugify(k)),
                    time=t,
                    tags=dict(
                        station_id=self.mac_address,
                        interface=str(self._id),
                    ),
                    fields=dict(
                        value=value
                    )
                ))




        #logging.info("==========indoor module==========")
        #logging.info(data["body"]["devices"][0]["dashboard_data"])

        for k,v in data["body"]["devices"][0]["dashboard_data"].iteritems():
            if k in self.KEYS:
                logging.info(k)
                value = self.parse_value(v)
                points.append(dict(
                    measurement="{}.indoor.{}".format(self.measurement_key, self.slugify(k)),
                    time=t,
                    tags=dict(
                        station_id=self.mac_address,
                        interface=str(self._id),
                    ),
                    fields=dict(
                        value=value
                    )
                ))
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
