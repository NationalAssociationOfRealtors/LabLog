from lablog.interfaces import Interface
from lablog import messages
import humongolus.field as field

class PhilipsHue(Interface):
    exchange = messages.Exchanges.node
    measurement_key = 'actuator.light'

    bridge_id = field.Char()
    access_token = field.Char()
    light_id = field.Integer()

    def data(self, data=None): pass

    def parse_data(self, data): pass
