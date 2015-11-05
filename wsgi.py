from gevent import monkey
monkey.patch_all()

from werkzeug.wsgi import peek_path_info
from geventwebsocket import Resource
from lablog import config
from lablog.app import App
from lablog.controllers.dashboard import dashboard
from lablog.controllers.auth import auth
from lablog.controllers.auth.facebook import facebook
from lablog.controllers.healthcheck import hc
from lablog.controllers.api.lab import lab
from lablog.controllers.api.node import node
from lablog.controllers.api.location import location
from lablog.controllers.reports import reports
from lablog.controllers.locations import locations
from lablog.app.kilo import Kilo
import logging
logging.basicConfig(level=config.LOG_LEVEL)

def healthcheck(app, env):
    if peek_path_info(env) == "healthcheck":
        app.config['SERVER_NAME'] = None
    else:
        app.config['SERVER_NAME'] = config.SERVER_NAME

def create_app():
    logging.info("Initializing")
    _app = App()
    ### Require Auth for Web App controllers ###
    dashboard.before_request(_app.user_logged_in)
    facebook.before_request(_app.user_logged_in)
    locations.before_request(_app.user_logged_in)
    ### Web App Controllers ###
    _app.register_blueprint(dashboard)
    _app.register_blueprint(auth)
    _app.register_blueprint(facebook)
    _app.register_blueprint(hc)
    _app.register_blueprint(reports)
    _app.register_blueprint(locations)
    ### API Controllers (OAuth protected)###
    _app.register_blueprint(location)
    _app.register_blueprint(lab)
    _app.register_blueprint(node)
    def app(env, start_response):
        #healthcheck(_app, env)
        return _app(env, start_response)

    logging.info("Running")
    return app

app = Resource(apps=[
    ('/', create_app()),
    ('/socket', Kilo),
])
