from bson.objectid import ObjectId
from lablog.triggers import Trigger, TriggerEnabled, TriggerDisabled
from lablog.models.location import Location
from lablog.hooks import post_slack, set_light
from datetime import datetime, timedelta
import logging

class CO2(Trigger):

    def post(self, val):
        post_slack.delay(message={"text":"Warning! C02 levels are elevated. {}PPM".format(val)})

    def turn_light_on(self, location):
        hue = location.get_interface('PhilipsHue')
        if not hue or not hue.bridge_id: return
        set_light.delay(
            bridge=hue.bridge_id,
            auth=hue.access_token,
            light=hue.light_id,
            command={
                'on':True,
                'bri':255,
                'sat':255,
                'hue':0,
            }
        )

    def turn_light_off(self, location):
        hue = location.get_interface('PhilipsHue')
        if not hue or not hue.bridge_id: return
        set_light.delay(
            bridge=hue.bridge_id,
            auth=hue.access_token,
            light=hue.light_id,
            command={
                'on':False,
                'bri':255,
                'sat':255,
                'hue':5000,
            }
        )

    def run(self, message):
        logging.info(message)
        location = Location.find_one({'interfaces.interface.id':ObjectId(message['tags']['interface'])})
        val = message['fields']['value']
        if val > 550:
            fiveminsago = datetime.utcnow()-timedelta(minutes=5)
            if fiveminsago > self.last_run:
                self.post(val)
                self.turn_light_on(location)
                raise TriggerEnabled(level=1)
        elif val < 550:
            fiveminsago = datetime.utcnow()-timedelta(minutes=5)
            if fiveminsago > self.last_run:
                self.turn_light_off(location)
                raise TriggerDisabled()

        return False
