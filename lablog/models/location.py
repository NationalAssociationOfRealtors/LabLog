import humongolus as orm
import humongolus.field as field
from lablog.util.tlcengine import TLCEngine
from lablog.util.odata import OData
from lablog import config
import logging

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
        if not self.meta.tlc or self.zipcode != self.meta.tlc.get('msa', {}).get('zip'):
            ret = {'msa':{'zip':self.zipcode}, 'vibes':{}}
            try:
                tlc = TLCEngine(un=config.TLC_UN, pw=config.TLC_PASSWORD)
                vibes = tlc.vibes(self.zipcode)

                for k,v in vibes.get('VibesData').items():
                    d = ret['msa'] if k.lower().startswith('msa') else ret['vibes']
                    try:
                        d[k] = float(v)
                    except Exception as e:
                        d[k] = v

                self.meta.tlc = ret
                self.save()
            except Exception as e:
                logging.error(e)
                self.meta.tlc = ret

        return self.meta.tlc['vibes']
