import os
import logging
import datetime

LOG_LEVEL = logging.INFO
DEBUG = True

HASH_ROUNDS = 3998
HASH_ALGO = "pbkdf2-sha512"
HASH_ALGO_CLS = "pbkdf2_sha512"
HASH_SALT_SIZE = 32

OAUTH_SCOPES = [
    u'analytics',
    u'inoffice',
]

OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 864000

ES_INDEX = "lablog"
ES_HOSTS = [{"host":"es", "port":9200},]

AUTH_SUBDOMAIN = "auth"

SECRET_KEY = "!!zer0K00L!!"
#SERVER_NAME = os.getenv("SERVER_NAME", "lablog.dev")

SESSION_COOKIE_NAME = "lablog"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None#".{}".format(SERVER_NAME)
SESSION_TYPE = 'mongodb'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=24)

REMEMBER_COOKIE_NAME = "well_hello_there"
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=5)
REMEMBER_COOKIE_DOMAIN = None#".{}".format(SERVER_NAME)

INFLUX_HOST = "influx"
INFLUX_PORT = 8086
INFLUX_USER = "root"
INFLUX_PASSWORD = "root"
INFLUX_DATABASE = "lablog"

LOGGER_NAME = "lablog"
JSON_AS_ASCII = False

TEMPLATES = "{}/lablog/views/templates".format(os.getcwd())

MONGO_HOST = "mongo"
MONGO_PORT = 27017

FACEBOOK_APP_ID = "805050686208884"#os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = "37c0f7647d6b85b589db7efb0a300a86"#os.getenv("FACEBOOK_APP_SECRET")
