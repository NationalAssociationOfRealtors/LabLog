import requests
from datetime import datetime

class OData(object):

    def __init__(self, url, un, pw):
        self.un = un
        self.pw = pw
        self.root_url = url
        self.params = {}

    def entity(self, entity):
        self.root_url = "{}/{}".format(self.root_url, entity)
        return self

    def id(self, id):
        self.root_url = "{}('{}')".format(self.root_url, id)
        return self.get()

    def filter(self, filters):
        self.params.setdefault('$filter', filters)
        return self

    def top(self, top):
        self.params.setdefault('$top', top)
        return self

    def orderby(self, orderby):
        self.params.setdefault('$orderby', orderby)
        return self

    def skip(self, skip):
        self.params.setdefault('$skip', skip)
        return self

    def parse_dates(self, res):
        def get_date(d):
            return datetime.fromtimestamp(int(d[6:-2])/1000)
        if isinstance(res, list):
            for i in res:
                print i
                for k,v in i.iteritems():
                    if isinstance(v, unicode) and v[1:5] == 'Date': i[k] = get_date(v)

        else:
            for k,v in res.iteritems():
                if isinstance(v, unicode) and v[1:5] == 'Date': res[k] = get_date(v)

        return res

    def get(self):
        print self.root_url
        print self.params
        res = requests.get(
            self.root_url,
            auth=(self.un, self.pw),
            params=self.params,
            headers={'accept':'application/json'}
        )
        j = res.json()
        return self.parse_dates(j.get('d', {}).get('results', j['d']))
