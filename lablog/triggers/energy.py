from lablog.triggers import Trigger, TriggerEnabled, TriggerDisabled
from lablog.hooks import post_slack
from datetime import datetime, timedelta

class InputFrequency(Trigger):

    def run(self, message):
        val = message['fields']['value']
        if val > 500:
            raise TriggerEnabled(level=1)
        elif val < 500:
            raise TriggerDisabled()

        return True
