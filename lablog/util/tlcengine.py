import requests

ROOT_URL =  "http://uatapiv2.tlcengine.com"

class TLCEngine(object):

    def __init__(self, un, pw):
        self.auth = self.auth(un, pw)
        self.access_token = self.auth.get('AccessToken')

    def auth(self, un, pw):
        url = "{}/{}".format(ROOT_URL, "/v2/api/nsmls/accesstokens/agents")
        res = requests.post(url, data={'Username': un, "Password":pw})
        return res.json()

    def vibes(self, zipcode):
        headers = {'Accept':'application/json', 'Authorization': 'bearer {}'.format(self.access_token)}
        url = "{}/{}".format(ROOT_URL, "/V2/api/nsmls/basedata/vibes")
        return requests.get(url, headers=headers, params={'zipcode':zipcode}).json()
