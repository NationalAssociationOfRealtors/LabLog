from flask import Blueprint, Response, render_template, request, g
from flask.views import MethodView
from lablog.app import App
from lablog import config
from lablog.util.jsontools import jsonify
from flask_oauthlib.provider import OAuth2Provider
import logging
from lablog.controllers.auth import oauth

lab = Blueprint(
    'lab',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/api/{}/lab".format(config.API_VERSION),
)

@lab.route("/me", methods=["GET"])
@oauth.require_oauth('inoffice')
def me():
    me = request.oauth.user.json()
    me['times'] = request.oauth.user.get_punchcard(g.INFLUX)
    return jsonify(me)

@lab.route("/team", methods=["GET"])
@oauth.require_oauth('inoffice')
def team():
    ret = []
    for user in request.oauth.client.users():
        u = user.json()
        u['times'] = user.get_punchcard(g.INFLUX)
        ret.append(u)

    return jsonify(ret)
