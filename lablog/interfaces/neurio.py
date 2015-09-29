from lablog.interfaces import Interface
from xml.etree import ElementTree as ET
from datetime import datetime
import requests
import logging

class HomeEnergyMonitor(Interface):

    def __init__(self, url, un, pw):
        self.url = "{}/both_tables.html".format(url)
        self.un = un
        self.pw = pw

    def data(self, data=None):
        auth = (self.un, self.pw) if self.un else None
        res = requests.get(self.url, auth=auth)
        return res.text

    def parse_data(self, data):
        ls = []
        for i in data.split("\r\n"):
            ls.append(i.strip())
        data = "".join(ls)
        data = data.split("</table>")
        logging.info(data)
        table1 = ET.XML("{}</table>".format(data[0]))
        table2 = ET.XML("{}</table>".format(data[1]))
        table1_rows = list(table1)
        table2_rows = list(table2)
        d = {}
        d['power'] = 0
        d['wattage'] = 0
        d['received'] = 0
        d['delivered'] = 0
        for row in table1_rows[2:]:
            d['wattage']+=float(row[1].text)

        for row in table2_rows[2:]:
            d['power']+=float(row[1].text)
            d['received']+=float(row[3].text)
            d['delivered']+=float(row[2].text)

        now = datetime.utcnow()
        points = [dict(
            measurement="energy.smartmeter.{}".format(k),
            time=now,
            tags=dict(
                macid=self.url,
            ),
            fields=dict(
                value=v
            ),
        ) for k,v in d.iteritems()]
        return points
