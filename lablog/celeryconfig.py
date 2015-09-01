from kombu import Exchange, Queue
import datetime

BROKER_URL = "amqp://guest:guest@mq"

CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_SERIALIZER = "json"

CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

CELERY_IMPORTS = (
    'lablog.workers',
)

default_q = Queue('default', Exchange('default'), routing_key='default')

CELERY_QUEUES = (
    default_q,
)

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_TIMEZONE = 'UTC'

CELERYBEAT_SCHEDULE = {
    'monitor_ups': {
        'task': 'lablog.workers.monitor_ups',
        'schedule': datetime.timedelta(minutes=1),
    },
}
