from werkzeug.wsgi import peek_path_info
from lablog import config
from lablog.app import App
from lablog.controllers.dashboard import dashboard
from lablog.controllers.auth import auth
from lablog.controllers.auth.facebook import facebook
from lablog.controllers.healthcheck import hc
import logging

def create_app():
    logging.basicConfig(level=config.LOG_LEVEL)
    logging.info("Initializing")
    _app = App()
    _app.configure_dbs()
    dashboard.before_request(_app.user_logged_in)
    facebook.before_request(_app.user_logged_in)
    _app.register_blueprint(dashboard)
    _app.register_blueprint(auth)
    _app.register_blueprint(facebook)
    _app.register_blueprint(hc)
    def app(env, start_response):
        #if peek_path_info(env) == "healthcheck":
        #    _app.config['SERVER_NAME'] = None
        #else:
        #    _app.config['SERVER_NAME'] = config.SERVER_NAME

        return _app(env, start_response)

    logging.info("Running")
    return app

app = create_app()
