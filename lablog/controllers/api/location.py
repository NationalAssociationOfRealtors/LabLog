from flask import Blueprint, Response, render_template, request, g, abort, current_app, session
from flask.views import MethodView
from lablog.app import App
from lablog import config
from lablog.util.jsontools import jsonify
from lablog import messages
from lablog.models.location import Location
from lablog.controllers.auth import oauth
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

@location.route("/<location_id>/current", methods=["GET"])
def location_current(location_id):
    loc = Location(id=location_id)
    ret = {}
    for i in loc.interfaces:
        inter = i._get('interface')._value.get('cls').split(".")[-1]
        if inter == "NetAtmo":
            r = i.interface.get_current(g.INFLUX)
            for k,v in r.iteritems():
                if k in ['netatmo.indoor.temperature', 'netatmo.indoor.humidity', 'netatmo.indoor.co2']:
                    ret[k.split(".")[-1]] = v['current'][0]['value']
            logging.info(ret)
            break

    return jsonify(ret)
