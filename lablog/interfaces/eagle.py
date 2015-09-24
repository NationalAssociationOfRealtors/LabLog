from lablog.interfaces import Interface
import requests
from datetime import datetime

class EnergyGateway(Interface):
    CMD = "<LocalCommand>\
            <Name>get_usage_data</Name>\
            <MacId>{macid}</MacId>\
        </LocalCommand>\
        <LocalCommand>\
            <Name>get_price_blocks</Name>\
            <MacId>{macid}</MacId>\
        </LocalCommand>\
        :"

    def __init__(self, macid, un, pw, address):
        self.macid = macid
        self.cmd = self.CMD.format(**{'macid':macid})
        self.url = "{}/cgi-bin/cgi_manager".format(address)
        self.un = un
        self.pw = pw

    def data(self, data=None):
        res = requests.post(self.url, auth=(self.un, self.pw), data=self.cmd)
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
            measurement="energy.smartmeter.{}".format(k),
            time=now,
            tags=dict(
                macid=self.macid,
            ),
            fields=dict(
                value=v
            ),
        ) for k,v in d.iteritems()]
        return points
