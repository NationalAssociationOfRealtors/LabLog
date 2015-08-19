from flask import Blueprint, Response, render_template, request
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
    url_prefix="/lab",
)

@lab.route("/me", methods=["GET"])
@oauth.require_oauth('inoffice')
def me():
    return jsonify(request.oauth.user.json())

@lab.route("/beacon", methods=["POST"])
@oauth.require_oauth('inoffice')
def beacon():
    return jsonify(request.oauth.user.json())

@lab.route("/team", methods=["GET"])
@oauth.require_oauth('inoffice')
def team():
    return jsonify([user.json() for user in request.oauth.client.users()])
