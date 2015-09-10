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
        power = float(data['demand'])
        received = float(data['summation_received'])
        delivered = float(data['summation_delivered'])
        price = float(data['price'])
        amps = power/240
        points = [dict(
            measurement="smartmeter",
            time=datetime.utcnow(),
            tags=dict(
                macid=self.macid,
            ),
            fields=dict(
                power=power,
                to_grid=received,
                from_grid=delivered,
                amps=amps,
                price=price,
            ),
        )]
        return points
