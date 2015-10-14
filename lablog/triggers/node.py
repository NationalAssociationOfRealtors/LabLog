from lablog.triggers import Trigger, TriggerEnabled, TriggerDisabled
from lablog.hooks import post_slack
from datetime import datetime, timedelta

class CO2(Trigger):

    def post(self):
        fiveminsago = datetime.utcnow()-timedelta(minutes=5)
        if fiveminsago > self.last_run:
            post_slack.delay(message={"text":"Warning! C02 levels are elevated. {}PPM".format(val)})

    def run(self, message):
        val = message['fields']['value']
        if val > 550:
            self.post()
            raise TriggerEnabled(level=1)
        elif val < 550:
            raise TriggerDisabled()

        return False
