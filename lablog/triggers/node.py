from lablog.triggers import Trigger
from lablog.hooks import post_slack
from datetime import datetime, timedelta

class CO2(Trigger):

    def run(self, message):
        fiveminsago = datetime.utcnow()-timedelta(minutes=5)
        val = message['fields']['value']
        if val > 400 and fiveminsago > self.last_run:
            post_slack.delay(message={"text":"Warning! C02 levels are elevated. {}PPM".format(val)})
            return True

        return False
