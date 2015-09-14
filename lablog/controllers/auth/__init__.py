from flask import Blueprint, render_template, flash, request, redirect, url_for, session, get_flashed_messages, current_app, jsonify
from flask.ext.login import login_user, current_user, logout_user, login_required
from flask.views import MethodView
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from passlib.hash import hex_sha1 as hex_sha1
from lablog import config
from lablog.app import App
from lablog.models.client import Client, Admin, Token, Grant, ClientRef
from lablog.util import password
from datetime import datetime, timedelta
from flask_oauthlib.provider import OAuth2Provider
import logging
import ldap

auth = Blueprint(
    'auth',
    __name__,
    template_folder=config.TEMPLATES,
    url_prefix="/auth",
)

app = App()
oauth = OAuth2Provider(app)

def ldap_login(un, pw):
    logging.info('ldap://{}:{}'.format(config.LDAP_HOST, config.LDAP_PORT))
    ld = ldap.initialize('ldap://{}:{}'.format(config.LDAP_HOST, config.LDAP_PORT))
    ld.protocol_version = ldap.VERSION3
    ld.set_option(ldap.OPT_REFERRALS, 0)
    ld.simple_bind_s(config.LDAP_USERNAME, config.LDAP_PASSWORD)
    r = ld.search(config.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, config.LDAP_USER_OBJECT_FILTER.format(un), ['displayName'])
    type,user = ld.result(r,60)
    logging.info(user)
    dn,attrs = user[0]
    logging.info(dn)
    ld.simple_bind_s(dn, pw)
    results = ld.search_s(config.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, config.LDAP_USER_OBJECT_FILTER.format(un), None)
    if len(results) > 1: raise Exception("Invalid Auth")
    return results[0][1]

class AuthLogin(MethodView):

    def get(self):
        logging.info("Next: {}".format(request.args.get("next")))
        return render_template("auth/login.html", next=request.args.get("next", url_for("dashboard.index")))

    def post(self):
        form = request.form
        un = form['username']
        pw = form['password']
        nex = form.get('next', url_for("dashboard.index"))
        logging.info("Next: {}".format(nex))
        if not config.LDAP_LOGIN:
            a = Admin.find_one({'email':un})
            if a and a.verify_pwd(pw):
                login_user(a)
                logging.info("logged in")
                return redirect(nex)
            else:
                flash("Please try again", "danger")

        else:
            try:
                user = ldap_login(un, pw)
                a = Admin.find_one({'email':user.get('mail')[0]})
                if not a: a = Admin()
                a.name = user.get('displayName')[0]
                a.email = user.get('mail')[0]
                a.last_login = datetime.utcnow()
                a.save()
                rem = False
                if form.get("remember-me"): rem = True
                success = login_user(a, remember=rem)
                return redirect(nex)
            except Exception as e:
                logging.exception(e)
                flash("Please try again", "danger")

        return render_template("auth/login.html", form=form)

class AuthRegister(MethodView):

    def get(self):
        return render_template("auth/register.html", clients=Client)

    def post(self):
        form = request.form
        pwd = form['password']
        cpwd = form['confirm_password']
        if not Admin.passwords_match(pwd, cpwd):
            flash("Passwords do not match", "danger")
            return render_template("auth/register.html", form=form)
        try:
            a = Admin()
            a.name = form['name']
            a.email = form['email']
            a.password = form['password']
            a.save()
        except DuplicateKeyError as e:
            logging.exception(e)
            flash("Email address already taken", "danger");
            return render_template("auth/register.html", form=form)

        login_user(a)
        return redirect(url_for("dashboard.index"))


class AuthLogout(MethodView):

    def get(self):
        logout_user()
        return redirect(url_for(".login"))

@oauth.clientgetter
def load_client(client_id):
    try:
        return Client(id=client_id)
    except: return None

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
    ua = request.environ.get('HTTP_USER_AGENT')
    if access_token:
        logging.info("Token {}".format(access_token))
        logging.info("Length {}".format(len(access_token)))
        logging.info("Token {}".format(refresh_token))
        t = Token.find_one({'access_token':access_token, 'user_agent':ua})
        return t
    elif refresh_token:
        return Token.find_one({'refresh_token':refresh_token})

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    ua = request.headers.get('User-Agent')
    toks = Token.find({
        'client':request.client._id,
        'user':current_user._id,
        'user_agent':ua,
    })
    for t in toks: t.remove()
    expires = datetime.utcnow() + timedelta(days=10)

    tok = Token()
    tok.access_token = token['access_token']
    tok.refresh_token = token.get('refresh_token', token['access_token'])
    tok._type = token['token_type']
    [tok.scopes.append(scope) for scope in token['scope'].split(" ")]
    tok.expires = expires
    tok.client = request.client
    tok.user = current_user
    tok.user_agent = ua
    tok.save()
    user = current_user
    add = True
    for c in user.clients:
        if c.ref._id == request.client._id: add = False
    if add:
        c = ClientRef()
        c.ref = request.client
        user.clients.append(c)
        user.save()
    return tok

@auth.route("/authorize", methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        logging.info(args)
        logging.info(kwargs)
        user = current_user
        client = Client(id=request.args.get('client_id', None))
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('auth/authorize.html', **kwargs)

    return True

@oauth.invalid_response
def invalid_require_oauth(req):
    return jsonify({'message':req.error_message}), 401

auth.add_url_rule("/login", view_func=AuthLogin.as_view('login'))
auth.add_url_rule("/logout", view_func=AuthLogout.as_view('logout'))
auth.add_url_rule("/register", view_func=AuthRegister.as_view('register'))
