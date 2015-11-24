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
    res = requests.post(config.SLACK_WEBHOOK, data=json.dumps(message))
    logging.info("Posted Slack: {}".format(res))
    logging.info(res.text)

@app.task
def set_light(bridge, auth, light, command):
    h = Hue(bridge_id=bridge, auth_token=auth)
    h.post('/lights/{}/state'.format(light), command)
