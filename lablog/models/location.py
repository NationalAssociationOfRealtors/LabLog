import humongolus as orm
import humongolus.field as field
from lablog.util.tlcengine import TLCEngine
from lablog.util.odata import OData
from lablog import config

class LocationMeta(orm.EmbeddedDocument):
    mls = orm.Field()
    tlc = orm.Field()

class LocationInterface(orm.EmbeddedDocument):

    interface = field.DynamicDocument()

class Location(orm.Document):
    _db = 'lablog'
    _collection = 'locations'

    name = field.Char()
    description = field.Char()
    geo = field.Geo()
    property_id = field.Char()
    interfaces = orm.List(type=LocationInterface)
    zipcode = field.Char()
    meta = LocationMeta()

    def get_interface_data(self, db, _from="7d"):
        vals = {}
        for i in self.interfaces:
            inter = i.interface
            vals[inter.__class__.__name__] = inter.get_values(db, _from)

        return vals

    def get_interface(self, interface):
        inte = None
        for i in self.interfaces:
            inter = i._get('interface')._value.get('cls').split(".")[-1]
            self.logger.info(inter)
            if inter == interface:
                inte = i.interface
                break
        return inte

    @property
    def mls(self):
        if not self.meta.mls or self.property_id != self.meta.mls.get('ListingId'):
            od = OData(config.MLS_ODATA_URL, config.MLS_ODATA_UN, config.MLS_ODATA_PASSWORD)
            res = od.entity("Property").id(self.property_id)#filter("PostalCode eq '60626'").orderby("ListingContractDate desc").top("1").get()
            self.meta.mls = res
            self.save()

        return self.meta.mls

    @property
    def tlc(self):
        if not self.meta.tlc:
            tlc = TLCEngine(un=config.TLC_UN, pw=config.TLC_PASSWORD)
            vibes = tlc.vibes(self.zipcode)
            tlc = {" ".join(k.split("_")):float(v) for k,v in vibes.get('VibesData').iteritems()}
            self.meta.tlc = tlc
            self.save()
        return self.meta.tlc
