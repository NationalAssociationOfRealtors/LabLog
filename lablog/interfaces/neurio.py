from lablog.interfaces import Interface
import humongolus.field as field
from xml.etree import ElementTree as ET
from datetime import datetime
from datetime import timedelta
from lablog import messages
import requests
import logging

class HomeEnergyMonitor(Interface):
    exchange = messages.Exchanges.energy
    measurement_key = "energy.smartmeter"
    run_delta = timedelta(seconds=30)

    url = field.Char()
    un = field.Char()
    pw = field.Char()

    def data(self, data=None):
        url = "{}/both_tables.html".format(self.url)
        auth = (self.un, self.pw) if self.un else None
        res = requests.get(url, auth=auth, timeout=5)
        return res.text

    def parse_data(self, data):
        ls = []
        for i in data.split("\r\n"):
            ls.append(i.strip())
        data = "".join(ls)
        data = data.split("</table>")
        logging.debug(data)
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
            measurement="{}.{}".format(self.measurement_key, k),
            time=now,
            tags=dict(
                macid=self.url,
                interface=str(self._id),
            ),
            fields=dict(
                value=v
            ),
        ) for k,v in d.iteritems()]
        return points
