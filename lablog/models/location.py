import humongolus as orm
import humongolus.field as field

class LocationInterface(orm.EmbeddedDocument):

    interface = field.DynamicDocument()

class Location(orm.Document):
    _db = 'lablog'
    _collection = 'locations'

    name = field.Char()
    description = field.Char()
    geo = field.Geo()
    interfaces = orm.List(type=LocationInterface)
