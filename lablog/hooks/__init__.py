from celery import Celery
from lablog import config
import requests
import logging
import json

app = Celery(__name__)
app.config_from_object('lablog.celeryconfig')

@app.task
def post_slack(message):
    res = requests.post(config.SLACK_WEBHOOK, data=json.dumps(message))
    logging.info("Posted Slack: {}".format(res))
    logging.info(res.text)
