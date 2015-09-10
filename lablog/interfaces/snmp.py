from snimpy.manager import Manager as M
from snimpy.manager import load
from lablog.interfaces import Interface

class SNMP(Interface):

    def __init__(self, mibs, ip, community, version):
        for i in mibs:
            load(i)
        self.manager = M(ip, community, version)
