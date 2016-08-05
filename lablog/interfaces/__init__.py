import humongolus as orm
import humongolus.field as field
from lablog import messages
from lablog.triggers import TriggerInstance
import datetime
import logging

class NotImplemented(Exception): pass
class NoData(Exception): pass

class Interface(orm.Document):
    _db = 'lablog'
    _collection = 'interfaces'
    exchange = None
    measurement_key = None
    run_delta = None#datetime.timedelta(minutes=5)

    _last_run = field.Date()
    _enabled = field.Boolean(default=True)

    def run(self, db, mq, data=None):
        now  = datetime.datetime.utcnow()
        if not self.run_delta:
            logging.info("No Delta")
            return
        if not self._last_run or ((now - self._last_run) >= self.run_delta):
            logging.info("Going")
            self.go(db, mq, data)
            logging.info("Updating last run")
            self._last_run = datetime.datetime.utcnow()
            self.save()
        else:
            logging.info("No need to run")
        return True

    def data(self, data=None):
        raise NotImplemented('data method should be overridden in subclass and return data')

    def parse(self, data):
        if not data: raise NoData()
        data = self.parse_data(data)
        return data

    def parse_data(self, data):
        raise NotImplemented('parse_data method should be overridden in subclass and needs to return parsed data')

    def log(self, data, db):
        db.write_points(data)

    def queue(self, data, mq, exchange):
        for i in data:
            key = i['measurement']
            messages.publish(mq, i, exchange, routing_key=key)

    def go(self, db, mq, data=None):
        raw_data = self.data(data=data)
        parsed_data = self.parse(raw_data)
        self.log(parsed_data, db)
        self.queue(parsed_data, mq, self.exchange)
        return parsed_data

    def get_long_history(self, db, _from):
        historical = "SELECT MEAN(value) as value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}' GROUP BY time(1d) fill(0)".format(self.measurement_key, _from, self._id)
        logging.info(historical)
        try:
            res = db.query(historical)
        except Exception as e:
            res = {}
        ret = {}
        for t,g in res.items():
            ret.setdefault(t[0], {})
            ret[t[0]] = {'historical': [p for p in g]}

        return ret

    def get_current(self, db):
        current = "SELECT LAST(value) as value FROM \"lablog\".\"realtime\"./{}.*/ WHERE interface='{}'".format(self.measurement_key, self._id)
        res = db.query(current)
        ret = {}
        for t,g in res.items():
            ret.setdefault(t[0], {})
            ret[t[0]].update({'current': [p for p in g]})
        return ret

    def get_values(self, db, _from):
        historical = "SELECT value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}'".format(self.measurement_key, _from, self._id)
        previous = "SELECT FIRST(value) as value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}'".format(self.measurement_key, _from, self._id)
        current = "SELECT LAST(value) as value FROM \"lablog\".\"realtime\"./{}.*/ WHERE interface='{}'".format(self.measurement_key, self._id)
        aggregate = "SELECT MIN(value) as min_value, MAX(value) as max_value, MEAN(value) as mean_value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}'".format(self.measurement_key, _from, self._id)
        triggers = TriggerInstance.find({'enabled':True, 'interface':str(self._id)})

        sql = "{};{};{};{}".format(historical, previous, current, aggregate)
        try:
            res = db.query(sql)
        except Exception as e:
            res = [{}, {}, {}, {}]
        ret = {}
        for t,g in res[0].items():
            ret.setdefault(t[0], {})
            ret[t[0]] = {'historical': [p for p in g]}
        for t,g in res[1].items():
            ret.setdefault(t[0], {})
            ret[t[0]].update({'previous': [p for p in g]})
        for t,g in res[2].items():
            ret.setdefault(t[0], {})
            ret[t[0]].update({'current': [p for p in g]})
        for t,g in res[3].items():
            ret.setdefault(t[0], {})
            ret[t[0]].update({'aggregate': [p for p in g]})

        logging.info("Triggers!")
        for t in triggers:
            logging.info(t.json())
            v = ret.get(t.key)
            if v: v.update({'trigger':t.level})

        return ret
