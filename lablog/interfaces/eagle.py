from lablog.interfaces import Interface
import humongolus.field as field
from lablog import messages
import requests
from datetime import datetime

class EnergyGateway(Interface):
    exchange = messages.Exchanges.energy
    measurement_key = "energy.smartmeter"

    CMD = "<LocalCommand>\
            <Name>get_usage_data</Name>\
            <MacId>{macid}</MacId>\
        </LocalCommand>\
        <LocalCommand>\
            <Name>get_price_blocks</Name>\
            <MacId>{macid}</MacId>\
        </LocalCommand>\
        :"


    macid = field.Char()
    un = field.Char()
    pw = field.Char()
    url = field.Char()

    def data(self, data=None):
        cmd = self.CMD.format(**{'macid':self.macid})
        url = "{}/cgi-bin/cgi_manager".format(self.url)
        res = requests.post(url, auth=(self.un, self.pw), data=cmd)
        return res.json()

    def parse_data(self, data):
        d = {}
        d['power'] = float(data['demand'])
        d['received'] = float(data['summation_received'])
        d['delivered'] = float(data['summation_delivered'])
        d['price'] = float(data['price'])
        d['amps'] = d['power']/240
        now = datetime.utcnow()
        points = [dict(
            measurement="{}.{}".format(self.measurement_key, k),
            time=now,
            tags=dict(
                macid=self.macid,
                interface=str(self._id),
            ),
            fields=dict(
                value=v
            ),
        ) for k,v in d.iteritems()]
        return points
