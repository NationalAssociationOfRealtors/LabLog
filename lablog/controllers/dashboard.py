from flask import Blueprint, Response, render_template, jsonify, url_for
from flask.views import MethodView
from passlib.hash import hex_sha1 as hex_sha1
from lablog.models.client import Client
from lablog.app import App
from lablog import config
from flask_oauthlib.provider import OAuth2Provider
import logging

dashboard = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

class Index(MethodView):
    def get(self):
        return render_template("index.html", client=Client)


class CreateClient(MethodView):
    def get(self, name):
        cl = Client()
        cl.name = name
        cl.secret = hex_sha1.encrypt(cl.name)
        cl._type = "public"
        cl.redirect_uris.append(unicode(url_for('dashboard.index', _external=True)))
        [cl.default_scopes.append(unicode(scope)) for scope in config.OAUTH_SCOPES]
        cl.save()
        return render_template("index.html", client=Client)


dashboard.add_url_rule("/", view_func=Index.as_view('index'))
dashboard.add_url_rule("/client/create/<name>", view_func=CreateClient.as_view('create_client'))
