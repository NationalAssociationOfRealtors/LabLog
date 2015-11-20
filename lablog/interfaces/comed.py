from lablog.interfaces import Interface
import humongolus.field as field
from xml.etree import ElementTree as ET
from datetime import datetime
from datetime import timedelta
from lablog import messages
import requests
import logging

class RTTP(Interface):
    exchange = messages.Exchanges.energy
    measurement_key = "energy.utility"
    run_delta = timedelta(seconds=30)

    url = field.Char()
    un = field.Char()
    pw = field.Char()

    def data(self, data=None):
        url = "{}".format(self.url)
        auth = (self.un, self.pw) if self.un else None
        res = requests.get(url, auth=auth, timeout=5, verify=False)
        return res.text

    def parse_data(self, data):
        price = float(data.split(">")[1].split("<")[0])
        now = datetime.utcnow()
        points = [dict(
            measurement="{}.{}".format(self.measurement_key, "price"),
            time=now,
            tags=dict(
                macid=self.url,
                interface=str(self._id),
            ),
            fields=dict(
                value=price
            ),
        )]
        return points
