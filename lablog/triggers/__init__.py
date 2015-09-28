import humongolus as orm
import humongolus.field as field
from bson.objectid import ObjectId
from datetime import datetime, timedelta


class Trigger(orm.Document):
    _db = "lablog"
    _collection = "triggers"

    _indexes = [
        orm.Index('name', key=('name', 1), unique=True),
    ]

    name = field.Char()
    key = field.Char()
    last_run = field.Date()
    _me = field.DynamicDocument()

    def save(self, *args, **kwargs):
        if not self._id:
            self._me = {}
            self.last_run = datetime.utcnow()-timedelta(minutes=60)
            super(Trigger, self).save(*args, **kwargs)
            self._me = self
        return super(Trigger, self).save(*args, **kwargs)

    def _run(self, message):
        ret = self._me.run(message)
        if ret:
            self.last_run = datetime.utcnow()
            self.save()
        return ret
