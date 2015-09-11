from flask import url_for
import humongolus as orm
import humongolus.field as field
import urllib, hashlib
from lablog.util import password

class PageCategory(orm.EmbeddedDocument):
    id = field.Char()
    name = field.Char()

class FacebookPage(orm.EmbeddedDocument):
    name = field.Char()
    token = field.Char()
    id = field.Char()
    permissions = orm.List(type=unicode)
    categories = orm.List(type=PageCategory)

class SocialAccount(orm.EmbeddedDocument):
    TWITTER = 'twitter'
    FACEBOOK = 'fb'
    GOOGLE = 'google'
    LINKEDIN = 'linkedin'

    type = field.Char()
    username = field.Char()
    id = field.Char()
    token = field.Char()
    secret = field.Char()
    avatar = field.Char()
    app_id = field.Char()
    permissions = orm.List(type=unicode)

class Client(orm.Document):
    _db = "lablog"
    _collection = "clients"

    _indexes = [
        orm.Index('name', key=('name', 1), unique=True),
    ]

    name = field.Char()
    description = field.Char()
    facebook_page = FacebookPage()
    secret = field.Char()
    redirect_uris = orm.List(type=unicode)
    default_scopes = orm.List(type=unicode)
    _type = field.Char()


    @property
    def client_type(self):
        return self._type;

    @property
    def default_redirect_uri(self):
        self.logger.info(self.redirect_uris)
        return self.redirect_uris[0]

class ClientRef(orm.EmbeddedDocument):
    ref = field.DocumentId(type=Client)

class Admin(orm.Document):
    _db = "lablog"
    _collection = "client_admins"
    _indexes = [
        orm.Index('email', key=('email', 1), unique=True),
    ]

    name = field.Char()
    email = field.Char()
    password = field.Char()
    last_login = field.Date()
    clients = orm.List(type=ClientRef)
    social_accounts = orm.List(type=SocialAccount)
    facebook_pages = orm.List(type=FacebookPage)
    in_office = field.Boolean(default=False)

    @staticmethod
    def passwords_match(pwd, cpwd):
        return pwd == cpwd

    def save(self):
        if self.password:
            if not password.identify(self.password):
                self.password = password.encrypt_password(self.password)
        return super(Admin, self).save()

    def verify_pwd(self, pwd):
        return password.check_password(pwd, self.password)

    def social_account(self, account_type=None):
        for sa in self.social_accounts:
            if sa.type == account_type: return sa
        sa = SocialAccount()
        sa.type = account_type
        return sa

    def get_punchcard(self, influx):
        try:
            res = influx.query("SELECT * from inoffice where user_id='{}' AND time > now() - 2d".format(self._id))
            r = [p for p in res.get_points()]
            r.reverse()
            return r
        except:
            return []

    def is_authenticated(self):
        if self._id: return True
        return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        self.logger.info(unicode(self._id))
        return unicode(self._id)


class Grant(orm.Document):
    _db = 'lablog'
    _collection = 'grants'
    client = field.DocumentId(type=Client)
    code = field.Char()
    user = field.DocumentId(type=Admin)
    scopes = orm.List(type=unicode)
    expires = field.Date()
    redirect_url = field.Char()

    def delete(self): self.remove()

class Token(orm.Document):
    _db = 'lablog'
    _collection = 'tokens'

    _indexes = [
        orm.Index('access_token', key=('access_token', 1), unique=True),
        orm.Index('refresh_token', key=('refresh_token', 1), unique=True),
        orm.Index('client', key=('client', 1)),
        orm.Index('user', key=('user', 1)),
        orm.Index('user_agent', key=('user_agent', 1)),
    ]

    access_token = field.Char()
    refresh_token = field.Char()
    client = field.DocumentId(type=Client)
    scopes = orm.List(type=unicode)
    expires = field.Date()
    user = field.DocumentId(type=Admin)
    user_agent = field.Char()
    _type = field.Char()

    @property
    def token_type(self):
        return self._type

    def delete(self): self.remove()

Client.users = orm.Lazy(type=Admin, key='clients.ref')
