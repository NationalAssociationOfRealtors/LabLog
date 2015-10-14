import humongolus as orm
import humongolus.field as field
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import logging

class TriggerEnabled(Exception):
    level = 0
    def __init__(self, level, message=None):
        super(TriggerEnabled, self).__init__(message)
        self.level = level

class TriggerDisabled(Exception): pass

class TriggerInstance(orm.Document):
    _db = "lablog"
    _collection = "trigger_instance"

    _indexes = [
        orm.Index('interface', key=('interface',1 ), unique=True),
        orm.Index('trigger', key=('trigger.id',1 )),
        orm.Index('enabled', key=('enabled',1 )),
        orm.Index('key', key=('key',1 )),
    ]

    enabled = field.Boolean(default=True)
    interface = field.Char()
    level = field.Integer()
    key = field.Char()

class Trigger(orm.Document):
    _db = "lablog"
    _collection = "triggers"

    _indexes = [
        orm.Index('name', key=('name', 1), unique=True),
        orm.Index('key', key=('key', 1)),
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
        interface = message['tags']['interface']
        try:
            ret = self._me.run(message)
        except TriggerEnabled as e:
            logging.info("Trigger Enabled")
            ti = TriggerInstance.find_one({'interface':interface, 'trigger.id':self._id})
            if not ti: ti = TriggerInstance()
            ti.enabled = True
            ti.interface = interface
            ti.level = e.level
            ti.key = self._me.key
            ti.trigger = self._me
            ti.save()
            self.last_run = datetime.utcnow()
            self.save()
        except TriggerDisabled as e:
            logging.info("Trigger Disabled")
            ti = TriggerInstance.find_one({'interface':interface, 'trigger.id':self._id})
            if not ti: return
            ti.enabled = False
            ti.save()

        return

TriggerInstance.trigger = field.DynamicDocument()
