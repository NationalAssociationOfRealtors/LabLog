from snimpy.manager import Manager as M
from snimpy.manager import load
from lablog.interfaces.snmp import SNMP
from lablog import messages
from datetime import datetime, timedelta

class UPS(SNMP):

    exchange = messages.Exchanges.energy
    measurement_key = "energy.ups"
    run_delta = timedelta(seconds=30)

    def data(self, data=None):
        for i in self.mibs.split(","): load(i)
        self.manager = M(self.ip, self.community, self.version)
        m = self.manager
        d = {}
        d['model'] = str(self.manager.upsIdentModel).strip()
        d['manufacturer'] = str(m.upsIdentManufacturer).strip()
        d['values'] = {}
        d['values']['battery_voltage'] = int(m.upsBatteryVoltage)
        d['values']['battery_current'] = int(m.upsBatteryCurrent)
        d['values']['input_frequency'] = []
        for l in m.upsInputFrequency:
            d['values']['input_frequency'].append(int(m.upsInputFrequency[l]))

        d['values']['input_voltage'] = []
        for l in m.upsInputVoltage:
            d['values']['input_voltage'].append(int(m.upsInputVoltage[l]))

        d['values']['output_current'] = []
        for l in m.upsOutputCurrent:
            d['values']['output_current'].append(int(m.upsOutputCurrent[l]))

        d['values']['output_power'] = []
        for l in m.upsOutputPower:
            d['values']['output_power'].append(int(m.upsOutputPower[l]))

        return d

    def point(self, data, key, val, line=None):
        t = datetime.utcnow()
        d = dict(
            measurement="{}.{}".format(self.measurement_key, key),
            time=t,
            tags=dict(
                model=data['model'],
                manufacturer=data['manufacturer'],
                interface=str(self._id),
            ),
            fields=dict(
                value=val
            ),
        )
        if line: d['tags']['line'] = line
        return d

    def parse_data(self, data):
        points = []
        for k,v in data['values'].iteritems():
            if isinstance(v, list):
                for line, i in enumerate(v):
                    points.append(self.point(data, k, i, line))
            else:
                points.append(self.point(data, k, v))

        return points
