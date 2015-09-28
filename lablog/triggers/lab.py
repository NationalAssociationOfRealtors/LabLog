from lablog.triggers import Trigger
from lablog.hooks import post_slack
from datetime import datetime, timedelta
from lablog.models.client import Admin
import logging

class Presence(Trigger):

    def run(self, message):
        logging.info("Received Presence Message: {}".format(message))
        user = Admin(id=message['tags']['user_id'])
        user.in_office = message['fields']['value']
        user.save();
        disp = "arrived" if user.in_office else "departed"
        post_slack.delay(message={"text":"{} has {}".format(user.name, disp)})
