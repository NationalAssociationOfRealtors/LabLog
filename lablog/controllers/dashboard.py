from flask import Blueprint, Response, render_template, jsonify, url_for
from flask.views import MethodView
from passlib.hash import hex_sha1 as hex_sha1
from lablog.models.client import Client
from lablog.models.location import Location
from lablog.util.tlcengine import TLCEngine
from lablog.app import App
from lablog import config
from flask_oauthlib.provider import OAuth2Provider
import logging

dashboard = Blueprint(
    'dashboard',
    __name__,
    template_folder=config.TEMPLATES,
)

def compare_tlc():
    diffs = {}
    for l in Location.find():
        vibes = l.tlc
        if isinstance(vibes, dict):
            for k,v in vibes.iteritems():
                if not isinstance(v,float): continue
                a = diffs.setdefault(k, {'min':999999, 'max':0})

                if v > a['max']: a['max'] = v
                if v < a['min']: a['min'] = v

            largest = {k:(v['max']-v['min']) for k,v in diffs.iteritems()}
            largest = sorted(largest.items(), cmp=lambda x,y: cmp(x[1], y[1]), reverse=True)

    return largest


class Index(MethodView):
    def get(self):
        largest = compare_tlc()
        return render_template("index.html", client=Client, location=Location, largest=largest)


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
