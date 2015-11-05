from flask import Flask, redirect, url_for, request, g
from flask_pjax import PJAX
from flask.ext.login import LoginManager, current_user
from flask.ext.session import Session
from pymongo.collection import Collection
import pymongo
from lablog.models.client import Admin
from lablog import config
from lablog import db
from slugify import slugify
import humongolus
import logging
import time

logging.basicConfig(level=config.LOG_LEVEL)

class App(Flask):

    def __init__(self):
        super(App, self).__init__(__name__)
        self.config.from_object('lablog.config')
        logging.info("SERVER_NAME: {}".format(self.config['SERVER_NAME']))
        self.before_request(self.init_dbs)
        self.teardown_request(self.teardown)
        self.after_request(self.teardown)
        try:
            self.init_session()
            self.init_login()
            self.init_pjax()
            self.init_templates()
        except Exception as e:
            logging.exception(e)

    def load_user(self, id):
        try:
            logging.info("Loading User: {}".format(id))
            a = Admin(id=id)
            return a
        except Exception as e:
            logging.exception(e)
            return None

    def init_templates(self):
        self.jinja_env.filters['slugify'] = slugify

    def teardown(self, exception):
        db = getattr(g, 'MONGO', None)
        if db is not None:
            db.close()

        if self.config.get('SESSION_MONGODB'):
            self.config['SESSION_MONGODB'].close()

        db = getattr(g, 'MQ', None)
        if db is not None:
            db.release()

        return exception

    def configure_dbs(self):
        es = db.init_elasticsearch()
        db.create_index(es)
        influx = db.init_influxdb()
        db.create_shards(influx)

    def init_dbs(self):
        g.ES = db.init_elasticsearch()
        g.INFLUX = db.init_influxdb()
        g.MONGO = db.init_mongodb()
        g.MQ = db.init_mq()
        humongolus.settings(logging, g.MONGO)

    def init_session(self):
        self.config['SESSION_MONGODB'] = db.init_mongodb()
        self.config['SESSION_MONGODB_DB'] = "app_sessions"
        self.config['SESSION_MONGODB_COLLECT'] = "sessions"
        self.config['SESSION_MONGODB']['app_sessions']['sessions'].create_index('id')
        Session(self)

    def init_login(self):
        self.login_manager = LoginManager()
        self.login_manager.init_app(self)
        self.login_manager.user_callback = self.load_user
        self.login_manager.login_view = "auth.login"

    def user_logged_in(self):
        logging.info(request.path)
        if not current_user.is_authenticated():
            return redirect(url_for("auth.login", next=request.path, _external=True, _scheme="https"))

    def init_pjax(self):
        PJAX(self)
