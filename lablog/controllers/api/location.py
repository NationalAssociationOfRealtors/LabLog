from flask import Blueprint, Response, render_template, request, g, abort, current_app, session
from flask.views import MethodView
from lablog.app import App
from lablog import config
from lablog.util.jsontools import jsonify
from lablog import messages
from lablog.models.location import Location
from datetime import datetime
import logging
import json

location = Blueprint(
    'location',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/api/{}/location".format(config.API_VERSION),
)

@location.route("/list", methods=["GET"])
@oauth.require_oauth('analytics')
def get_locations():
    locs = []
    for loc in Location.find():
        j = loc.json()
        net = loc.get_interface('NetAtmo')
        j['current'] = net.get_current(g.INFLUX) if net else {}
        locs.append(j)
    return jsonify(locs)

@location.route("/<location_id>", methods=["GET"])
@oauth.require_oauth('analytics')
def location_data(location_id):
    loc = Location(id=location_id)
    data = loc.get_interface_data(g.INFLUX)
    return jsonify({'location':loc.json(), 'data':data})
