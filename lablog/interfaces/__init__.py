from lablog import messages
import logging

class NotImplemented(Exception): pass
class NoData(Exception): pass

class Interface(object):

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

    def queue(self, data, mq, exchange, routing_key):
        for i in data:
            key = routing_key.format(**i)
            messages.publish(mq, i, exchange, routing_key=key)

    def go(self, db, mq, exchange, routing_key, data=None):
        raw_data = self.data(data=data)
        parsed_data = self.parse(raw_data)
        self.log(parsed_data, db)
        self.queue(parsed_data, mq, exchange, routing_key)
        return parsed_data
