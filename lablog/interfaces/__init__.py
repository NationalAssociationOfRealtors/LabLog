import humongolus as orm
from lablog import messages
import logging

class NotImplemented(Exception): pass
class NoData(Exception): pass

class Interface(orm.Document):
    _db = 'lablog'
    _collection = 'interfaces'
    exchange = None
    measurement_key = None

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

    def get_values(self, db, _from):
        historical = "SELECT value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}'".format(self.measurement_key, _from, self._id)
        previous = "SELECT FIRST(value) as value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}'".format(self.measurement_key, _from, self._id)
        current = "SELECT LAST(value) as value FROM \"lablog\".\"realtime\"./{}.*/ WHERE interface='{}'".format(self.measurement_key, self._id)
        aggregate = "SELECT MIN(value) as min_value, MAX(value) as max_value, MEAN(value) as mean_value FROM \"lablog\".\"1hour\"./{}.*/ WHERE time > now() - {} AND interface='{}'".format(self.measurement_key, _from, self._id)
        sql = "{};{};{};{}".format(historical, previous, current, aggregate)
        res = db.query(sql)
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

        return ret
