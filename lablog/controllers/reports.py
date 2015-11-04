from flask import Blueprint, Response, render_template, jsonify, url_for, g
from flask.views import MethodView
from passlib.hash import hex_sha1 as hex_sha1
from lablog.models.client import Client
from lablog.app import App
from lablog import config
from flask_oauthlib.provider import OAuth2Provider
from lablog.models.location import Location
from lablog.interfaces.eagle import EnergyGateway
from lablog.interfaces.netatmo import NetAtmo
from lablog.interfaces.neurio import HomeEnergyMonitor
from lablog.interfaces.presence import Presence
from lablog.interfaces.sensornode import Node
from lablog.interfaces.ups import UPS
from lablog.interfaces.wunderground import Wunderground
from lablog.messages import Exchanges
import logging

reports = Blueprint(
    'reports',
    __name__,
    template_folder=config.TEMPLATES,
)

def get_node_index(l, id):
    for i, obj in enumerate(l):
        if obj.get('id') == id: return i
    return None

def get_indexes_startswith(l, key):
    return [i for i, obj in enumerate(l) if obj.get('id').startswith(key)]

class DataFlowView(MethodView):

    def get(self):
        return render_template("reports/dataflow.html")

class DataFlow(MethodView):

    def get(self):
        locations = [loc for loc in Location.find()]
        interfaces = [EnergyGateway, NetAtmo, HomeEnergyMonitor, Presence, Node, UPS, Wunderground]
        exchanges = [Exchanges.node, Exchanges.energy, Exchanges.weather, Exchanges.presence, Exchanges.everything]
        final = ['Clients', 'Triggers', 'Federation']
        fnodes = []
        links = []
        res = g.INFLUX.query("SHOW MEASUREMENTS")
        measurements = [i for i in res.items()[0][1]]
        for f in final:
            fnodes.append({
                'name':f,
                'id':"final.{}".format(f),
                'type':'final',
            })
        for m in measurements:
            fnodes.append({
                'name':m['name'].split(".")[-1],
                'id':"data.{}".format(m['name']),
                'type':'data',
            })

        for i in interfaces:
            fnodes.append({
                'name':i.__name__,
                'id':"interface.{}.{}".format(i.exchange.name, i.__name__),
                'type':'interface',
            })

        for e in exchanges:
            fnodes.append({
                'name':e.name,
                'id':"exchange.{}".format(e.name),
                'type':'exchange',
            })

        ev_id = get_node_index(fnodes, 'exchange.everything')
        for loc in locations:
            fnodes.append({
                'name':loc.name,
                'id':str(loc._id),
                'type':'location'
            })
            links.append({
                'source':len(fnodes)-1,
                'target':get_node_index(fnodes, 'interface.presence.Presence'),
                'value':.01
            })
            for i in loc.interfaces:
                if not i.interface._last_run: continue
                e_name = i.interface.exchange.name
                i_index = get_node_index(fnodes, "interface.{}.{}".format(e_name, i.interface.__class__.__name__))
                e_id = get_node_index(fnodes, "exchange.{}".format(e_name))
                links.append({
                    'source':len(fnodes)-1,
                    'target':i_index,
                    'value':.01,
                })
                data_points = get_indexes_startswith(fnodes, "data.{}".format(i.interface.measurement_key))
                for dp in data_points:
                    links.append({
                        'source':i_index,
                        'target':dp,
                        'value':.01
                    })
                    links.append({
                        'source':dp,
                        'target':e_id,
                        'value':.01
                    })
                    links.append({
                        'source':dp,
                        'target':ev_id,
                        'value':.01
                    })

        links.append({
            'source':get_node_index(fnodes, 'exchange.energy'),
            'target':get_node_index(fnodes, 'final.Clients'),
            'value':.01
        })
        links.append({
            'source':get_node_index(fnodes, 'exchange.presence'),
            'target':get_node_index(fnodes, 'final.Clients'),
            'value':.01
        })
        links.append({
            'source':get_node_index(fnodes, 'exchange.node'),
            'target':get_node_index(fnodes, 'final.Clients'),
            'value':.01
        })
        links.append({
            'source':get_node_index(fnodes, 'exchange.weather'),
            'target':get_node_index(fnodes, 'final.Clients'),
            'value':.01
        })
        links.append({
            'source':get_node_index(fnodes, 'exchange.everything'),
            'target':get_node_index(fnodes, 'final.Triggers'),
            'value':.01
        })
        links.append({
            'source':get_node_index(fnodes, 'exchange.everything'),
            'target':get_node_index(fnodes, 'final.Federation'),
            'value':.01
        })
        io = get_node_index(fnodes, 'data.inoffice')
        if not io:
            fnodes.append({
                'name':'inoffice',
                'id':'data.inoffice',
                'type':'data'
            })
            io = len(fnodes)-1

        links.append({
            'source':get_node_index(fnodes, 'interface.presence.Presence'),
            'target':io,
            'value':.01
        })
        links.append({
            'source':io,
            'target':get_node_index(fnodes, 'exchange.presence'),
            'value':.01
        })
        links.append({
            'source':io,
            'target':ev_id,
            'value':.01
        })


        logging.info(links)

        return jsonify({'nodes':fnodes, 'links':links})

reports.add_url_rule("/dataflow", view_func=DataFlowView.as_view('dataflow'))
reports.add_url_rule("/dataflow/data", view_func=DataFlow.as_view('dataflow_data'))
