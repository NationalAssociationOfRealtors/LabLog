from flask import Blueprint, Response, render_template, jsonify, url_for, request, flash, redirect, g
from flask.views import MethodView
from lablog.models.location import Location, LocationInterface
from lablog.interfaces.eagle import EnergyGateway
from lablog.interfaces.neurio import HomeEnergyMonitor
from lablog.interfaces.netatmo import NetAtmo
from lablog.interfaces.sensornode import Node
from lablog.interfaces.presence import Presence
from lablog.interfaces.ups import UPS
from lablog.interfaces.wunderground import Wunderground
from lablog.interfaces.comed import RTTP
from lablog.interfaces.philipshue import PhilipsHue
from datetime import datetime, timedelta
from lablog import config
from humongolus import Field
import logging

interfaces = {
    EnergyGateway.__name__: EnergyGateway,
    HomeEnergyMonitor.__name__: HomeEnergyMonitor,
    Presence.__name__: Presence,
    NetAtmo.__name__: NetAtmo,
    Node.__name__: Node,
    UPS.__name__: UPS,
    Wunderground.__name__: Wunderground,
    RTTP.__name__: RTTP,
    PhilipsHue.__name__:PhilipsHue,
}

locations = Blueprint(
    'locations',
    __name__,
    template_folder=config.TEMPLATES,
)

class LocationController(MethodView):
    def get(self, id=None):
        if id:
            loc = Location(id=id)
            ints = {interface.interface.__class__.__name__: interface.interface for interface in loc.interfaces}
            for k,v in interfaces.iteritems():
                if not ints.get(k): ints.update({k: v()})
        else:
            loc = Location()
            ints = {key: value() for (key, value) in interfaces.iteritems()}

        return render_template("locations/create.html", location=loc, interfaces=ints)

    def post(self):
        vals = {}
        for k,v in request.form.iteritems():
            keys = k.split(".")
            vals.setdefault(keys[0], {})
            vals[keys[0]][keys[1]] = v

        loc_data = vals.pop("location")
        id = loc_data.pop("_id")
        if id:
            loc = Location(id=id)
            loc._map(loc_data)
        else:
            loc = Location(data=loc_data)
        for k,v in vals.iteritems():
            for i in loc.interfaces:
                inter = i.interface
                if inter.__class__.__name__ == k:
                    inter._map(v)
                    inter.save()
                    break
            else:
                i = interfaces.get(k)(data=v)
                i.save()
                li = LocationInterface()
                li.interface = i
                loc.interfaces.append(li)

        loc.save()
        logging.info(loc.json())
        flash("Saved!", "success")
        return redirect(url_for('.location', id=loc._id))

class LocationProperty(MethodView):

    def get(self, location):
        loc = Location(id=location)
        return render_template("locations/property.html", loc=loc, Location=Location)

class LocationWidget(MethodView):

    def get(self, location, interface):
        loc = Location(id=location)
        aq = {}
        power = {}
        cost = {}
        last = datetime.utcnow()-timedelta(hours=30)
        for l in loc.interfaces:
            n = l._get('interface')._value.get('cls').split(".")[-1]
            if n == interface:
                aq = l.interface.get_long_history(db=g.INFLUX, _from="12d")
            if n in ['EnergyGateway', 'HomeEnergyMonitor']:
                if l.interface._last_run and l.interface._last_run > last:
                    last = l.interface._last_run
                    power = l.interface.get_long_history(db=g.INFLUX, _from="12d")
            if n in ['RTTP']:
                cost = l.interface.get_long_history(db=g.INFLUX, _from="12d")


        return render_template("locations/widgets/{}.html".format(interface), data=aq, power=power, interface=interface, cost=cost)

locations.add_url_rule("/location", view_func=LocationController.as_view('create_location'))
locations.add_url_rule("/location/<id>", view_func=LocationController.as_view('location'))
locations.add_url_rule("/location/<location>/property", view_func=LocationProperty.as_view('location_property'))
locations.add_url_rule("/location/<location>/interface/<interface>", view_func=LocationWidget.as_view('location_widget'))
