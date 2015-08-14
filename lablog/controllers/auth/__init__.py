from flask import Blueprint, render_template, flash, request, redirect, url_for, session, get_flashed_messages, current_app
from flask.ext.login import login_user, current_user, logout_user, login_required
from flask.views import MethodView
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from passlib.hash import hex_sha1 as hex_sha1
from lablog import config
from lablog.app import App
from lablog.models.client import Client, Admin, Token, Grant
from lablog.util import password
from datetime import datetime, timedelta
from flask_oauthlib.provider import OAuth2Provider
import logging

auth = Blueprint(
    'auth',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/auth",
)

oauth = OAuth2Provider(App())

class AuthLogin(MethodView):

    def get(self):
        return render_template("auth/login.html")

    def post(self):
        form = request.form
        em = form['email']
        pw = form['password']
        a = Admin.find_one({'email':em})
        v = a.verify_pwd(pw)
        if a and v:
            rem = False
            if form.get("remember-me"): rem = True
            success = login_user(a, remember=rem)
            return redirect(url_for(".authorize", client_id=str(a.client._id), response_type='token'))
        else:
            flash("Please try again", "danger")

        return render_template("auth/login.html", form=form)

class AuthRegister(MethodView):

    def get(self):
        return render_template("auth/register.html")

    def post(self):
        form = request.form
        pwd = form['password']
        cpwd = form['confirm_password']
        if not Admin.passwords_match(pwd, cpwd):
            flash("Passwords do not match", "danger")
            return render_template("auth/register.html", form=form)
        try:
            cl = Client()
            cl.name = form['org']
            cl.secret = hex_sha1.encrypt(cl.name)
            cl._type = "public"
            cl.redirect_uris.append(unicode(url_for('dashboard.index', _external=True)))
            [cl.default_scopes.append(unicode(scope)) for scope in config.OAUTH_SCOPES]
            logging.info(cl.json())
            logging.info(cl.json())
            cl.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Organization name already taken", "danger");
            return render_template("auth/register.html", form=form)
        try:
            a = Admin()
            a.name = form['name']
            a.email = form['email']
            a.password = form['password']
            a.client = cl
            a.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Email address already taken", "danger");
            return render_template("auth/register.html", form=form)

        login_user(a)
        return redirect(url_for(".authorize", client_id=str(cl._id), response_type='token'))


class AuthLogout(MethodView):

    def get(self):
        logout_user()
        return redirect(url_for(".login"))

@oauth.clientgetter
def load_client(client_id):
    return Client(id=client_id)

@oauth.grantgetter
def grant_getter(client_id, code):
    return Grant.find_one({'client':ObjectId(client_id), 'code':code})

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    grant = Grant()
    grant.client = Client(id=client_id)
    grant.code = code['code']
    grant.redirect_uri = request.redirect_uri
    grant.scopes = request.scopes
    grant.user = current_user
    grant.expires = datetime.utcnow() + timedelta(days=10)
    grant.save()
    return grant

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        print "Access Token: {}".format(access_token)
        print "Refresh Token: {}".format(refresh_token)
        t = Token.find_one({'access_token':access_token})
        print t.json()
        return t
    elif refresh_token:
        return Token.find_one({'refresh_token':refresh_token})

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.find({
        'client':request.client._id,
        'user':current_user._id,
    })
    for t in toks: t.remove();

    expires = datetime.utcnow() + timedelta(days=10)

    tok = Token()
    tok.access_token = token['access_token']
    tok.refresh_token = token.get('refresh_token', token['access_token'])
    tok._type = token['token_type']
    tok.scopes = token['scope'].split(" ")
    tok.expires = expires
    tok.client = request.client
    tok.user = current_user
    tok.save()
    return tok

@auth.route("/authorize", methods=['GET', 'POST'])
@oauth.authorize_handler
@login_required
def authorize(*args, **kwargs):
    if request.method == 'GET':
        user = current_user
        client = user.client
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('auth/authorize.html', **kwargs)

    print "YAY"
    return True

@auth.route("/hello", methods=["GET"])
@oauth.require_oauth()
def hello():
    return jsonify({'hello':request.oauth.user.name})

auth.add_url_rule("/login", view_func=AuthLogin.as_view('login'))
auth.add_url_rule("/logout", view_func=AuthLogout.as_view('logout'))
auth.add_url_rule("/register", view_func=AuthRegister.as_view('register'))
