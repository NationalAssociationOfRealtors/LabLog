from flask import Blueprint, Response, render_template, jsonify, url_for
from flask.views import MethodView
from passlib.hash import hex_sha1 as hex_sha1
from lablog.models.client import Client
from lablog.app import App
from lablog import config
from lablog import dataflow
from flask_oauthlib.provider import OAuth2Provider
import logging

reports = Blueprint(
    'reports',
    __name__,
    template_folder=config.TEMPLATES,
)

class DataFlowView(MethodView):

    def get(self):
        return render_template("reports/dataflow.html")

class DataFlow(MethodView):

    def get(self):
        fnodes = []
        links = []
        for e, exchange in enumerate(dataflow.exchanges):
            nodes = []
            for i in exchange['nodes']:
                nodes.append({
                    'name':i,
                    'id':"{}_{}".format(
                        exchange['name'].lower().replace(" ", "_"),
                        i.lower().replace(" ", "_")
                    ),
                    'type':'interface'
                })
            data = []
            for d in exchange['data']:
                data.append({
                    'name':d,
                    'id':"{}_{}".format(
                        exchange['name'].lower().replace(" ", "_"),
                        d.lower().replace(" ", "_")
                    ),
                    'type':'data'
                })
            for ni,n in enumerate(nodes):
                for ii,d in enumerate(data):
                    links.append({
                        'source':len(fnodes)+ni,
                        'target':len(fnodes)+len(nodes)+ii,
                        'value':.01
                    })
            fnodes+=nodes
            fnodes+=data
            for ii, d in enumerate(data):
                links.append({
                    'source':(len(fnodes)-len(data))+ii,
                    'target':len(fnodes),
                    'value':.01,
                })
            fnodes.append({
                'name':exchange['name'],
                'id': exchange['name'].lower().replace(" ", "_"),
                'type':'exchange',
            })

        fnodes.append({
            'name':'Everything',
            'id': 'everything',
            'type': 'exchange_everything',
        })

        ev = len(fnodes)-1
        for i, n in enumerate(fnodes):
            if n['type'] == 'data':
                links.append({
                    'source':i,
                    'target':len(fnodes)-1,
                    'value':.01,
                })

        links.append({
            'source':ev,
            'target': len(fnodes),
            'value': .01,
        })
        fnodes.append({
            'name':"Triggers",
            'id':"triggers",
            'type':'trigger',
        })

        links.append({
            'source':ev,
            'target': len(fnodes),
            'value': .01,
        })
        fnodes.append({
            'name':"Federation",
            'id':"federation",
            'type':'deferation',
        })

        fnodes.append({
            'name': 'Clients',
            'id': 'clients',
            'type': 'clients',
        })
        for i, n in enumerate(fnodes):
            if n['type'] == 'exchange':
                links.append({
                    'source':i,
                    'target':len(fnodes)-1,
                    'value':.01,
                })

        return jsonify({'nodes':fnodes, 'links':links})

reports.add_url_rule("/dataflow", view_func=DataFlowView.as_view('dataflow'))
reports.add_url_rule("/dataflow/data", view_func=DataFlow.as_view('dataflow_data'))
