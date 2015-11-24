from lablog.interfaces import Interface
import humongolus.field as field

class PhilipsHue(Interface):
    exchange = None
    measurement_key = None

    bridge_id = field.Char()
    access_token = field.Char()
    light_id = field.Integer()

    def data(self, data=None): pass

    def parse_data(self, data): pass
