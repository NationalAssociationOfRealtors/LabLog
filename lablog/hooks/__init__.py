from celery import Celery
from lablog import config
import requests
from lablog.util.philipshue import Hue
import logging
import json

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')

@app.task
def post_slack(message):
    try:
        res = requests.post(config.SLACK_WEBHOOK, data=json.dumps(message), timeout=5)
        logging.info("Posted Slack: {}".format(res))
        logging.info(res.text)
    except Exception as e:
        logging.error(e)

@app.task
def set_light(bridge, auth, light, command):
    try:
        h = Hue(bridge_id=bridge, auth_token=auth)
        h.post('/lights/{}/state'.format(light), command)
    except Exception as e:
        logging.error(e)
