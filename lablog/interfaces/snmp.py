from lablog.interfaces import Interface
import humongolus.field as field

class SNMP(Interface):

    mibs = field.Char()
    ip = field.Char()
    community = field.Char()
    version = field.Integer()
