import os
import logging
import datetime

LOG_LEVEL = logging.INFO
logging.basicConfig(level=LOG_LEVEL)
DEBUG = True

BROKER_URL = "amqp://guest:guest@mq"

API_VERSION = "v1.0"

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

HUE_URL = "https://www.meethue.com/api/sendmessage"

AUTH_SUBDOMAIN = "auth"

SECRET_KEY = os.getenv("SECRET_KEY")
SERVER_NAME = os.getenv("SERVER_NAME")

SESSION_COOKIE_NAME = "lablog"
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = ".{}".format(SERVER_NAME) if SERVER_NAME else None
SESSION_TYPE = 'mongodb'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=24)

REMEMBER_COOKIE_NAME = "well_hello_there"
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=5)
REMEMBER_COOKIE_DOMAIN = ".{}".format(SERVER_NAME) if SERVER_NAME else None

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

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")

SKEY = os.environ.get("SKEY")

LDAP_LOGIN = True
LDAP_HOST = os.environ.get('LDAP_HOST')
LDAP_PORT = os.environ.get('LDAP_PORT')
LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN')
LDAP_USERNAME = os.environ.get('LDAP_USERNAME')
LDAP_PASSWORD = os.environ.get('LDAP_PASSWORD')
LDAP_USER_OBJECT_FILTER = os.environ.get('LDAP_USER_OBJECT_FILTER')

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

NETATMO_CLIENT_ID = os.environ.get('NETATMO_CLIENT_ID')
NETATMO_CLIENT_SECRET = os.environ.get('NETATMO_CLIENT_SECRET')
NETATMO_USERNAME = os.environ.get('NETATMO_USERNAME')
NETATMO_PASSWORD = os.environ.get('NETATMO_PASSWORD')

TLC_UN = os.environ.get('TLC_UN')
TLC_PASSWORD = os.environ.get('TLC_PASSWORD')

MLS_ODATA_URL = "http://connectmls-api.mredllc.com/RESO/Odata"
MLS_ODATA_UN = os.environ.get('MLS_ODATA_UN')
MLS_ODATA_PASSWORD = os.environ.get('MLS_ODATA_PASSWORD')
