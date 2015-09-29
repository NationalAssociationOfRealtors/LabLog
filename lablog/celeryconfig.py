from lablog import messages
from lablog import config
from lablog import db
import humongolus
import datetime
import logging

logging.basicConfig(level=config.LOG_LEVEL)

MONGO = db.init_mongodb()
humongolus.settings(logging, MONGO)

BROKER_URL = config.BROKER_URL

CELERY_ACCEPT_CONTENT = ['pickle']

CELERY_TASK_SERIALIZER = "pickle"

CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

CELERY_IMPORTS = (
    'lablog.workers',
    'lablog.hooks',
)

CELERY_QUEUES = (
    messages.Queues.tasks,
)

CELERY_DEFAULT_QUEUE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'tasks'
CELERY_TIMEZONE = 'UTC'

#CELERY_REDIRECT_STDOUTS_LEVEL = INFO

CELERYBEAT_SCHEDULE = {
    'monitor_ups': {
        'task': 'lablog.workers.monitor_ups',
        'schedule': datetime.timedelta(minutes=1),
    },
    'monitor_weather': {
        'task': 'lablog.workers.get_weather_data',
        'schedule': datetime.timedelta(minutes=4),
    },
    'monitor_smart_meter': {
        'task': 'lablog.workers.get_smartmeter_data',
        'schedule': datetime.timedelta(seconds=30),
    },
    'monitor_neurio_meter': {
        'task': 'lablog.workers.get_neurio_data',
        'schedule': datetime.timedelta(seconds=30),
    },
}
