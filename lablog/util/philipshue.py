import requests
import json
from lablog import config

class Hue(object):

    def __init__(self, bridge_id, auth_token):
        self.bridge_id = bridge_id
        self.auth_token = auth_token

    def message(self, end_point, command):
        msg = {
            'bridgeId':self.bridge_id,
            'clipCommand':{
                'url':"/api/0{}".format(end_point),
                'method':'PUT',
                'body':command,
            }
        }
        return msg

    def post(self, path, params):
        msg = self.message(path, params)
        res = requests.post(
            config.HUE_URL,
            params={'token':self.auth_token},
            headers = {'content-type':'application/x-www-form-urlencoded'},
            data='clipmessage={}'.format(json.dumps(msg)),
            timeout=5,
        )
        return res.text
