from flask import Blueprint, Response, render_template, request, g
from flask.views import MethodView
from lablog.app import App
from lablog import config
from lablog.util.jsontools import jsonify
from flask_oauthlib.provider import OAuth2Provider
import logging
from lablog.controllers.auth import oauth
from datetime import datetime

node = Blueprint(
    'node',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/node",
)

@node.route("/<node_id>/sensors", methods=["POST"])
def node_sensors(node_id):
    points = []
    for k,v in request.json.iteritems():
        p = dict(
            measurement=k,
            tags=dict(
                node=str(node_id),
            ),
            time=datetime.utcnow(),
            fields=dict(
                value=v
            )
        )
        g.MONGO['lablog']['node_stream'].insert(p)
        points.append(p)

    g.INFLUX.write_points(points)
    return jsonify({'success':True})
