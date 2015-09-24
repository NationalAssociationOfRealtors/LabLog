from lablog.interfaces import Interface
from datetime import datetime
import requests

class Wunderground(Interface):
    KEYS = ['UV', 'dewpoint_c', 'feelslike_c', 'heatindex_c', 'precip_1hr_metric',
        'precip_today_metric', 'pressure_in', 'pressure_mb', 'relative_humidity',
        'solarradiation', 'temp_c', 'visibility_km', 'wind_degrees', 'wind_gust_kph',
        'wind_kph', 'windchill_c']

    def __init__(self, api_key, station_id):
        self.station_id = station_id
        self.current_conditions = "http://api.wunderground.com/api/{}/conditions/q/pws:{}.json".format(api_key, station_id)

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

    def data(self, data=None):
        res = requests.get(self.current_conditions)
        return res.json()

    def parse_data(self, data):
        points = []
        t = datetime.utcnow()
        for k,v in data.get('current_observation').iteritems():
            if k in self.KEYS:
                value = self.parse_value(v)
                points.append(dict(
                    measurement="weather.{}".format(self.slugify(k)),
                    time=t,
                    tags=dict(
                        station_id=self.station_id,
                    ),
                    fields=dict(
                        value=value
                    )
                ))
        return points
