# coding=utf-8
import itertools

from flask.ext.login import AnonymousUserMixin
from werkzeug.datastructures import ImmutableList
from zch_logger import setup
from flask import abort
from functools import wraps

from functools import partial
from werkzeug.contrib.fixers import ProxyFix
from flask.ext import login
from flask.ext.babelex import Babel
from flask import url_for, redirect, flash
from flask import request, session, Flask

from wowhua_admin.cache import cache
from wowhua_admin.db_session import admin_session
from wowhua_admin.db_session import api_session
from wowhua_admin.db_session import aux_session
from wowhua_admin.db_session import session_init
from wowhua_admin.views import admin_handlers
from wowhua_admin.extensions import db as mongo_db
from wowhua_admin.models import AdminUser, AuthGroup, AuthPermission
from wowhua_admin.config import get_config
from wowhua_admin.admin import setup_admin
from wowhua_admin.util import on_models_committed
from wowhua_admin.extensions import admin

VALID_LOCALES = ['zh', 'en']

log_env = setup()
log_env.push_application()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

config = get_config()
app.config.update(dict(config))

#app.config['SECURITY_UNAUTHORIZED_VIEW'] = '/'
#app.config['SECURITY_MSG_UNAUTHORIZED'] = 'bbbbb'

cache.init_app(app)
app.register_blueprint(admin_handlers)

# register listener for signal of sqla
session_init(app, on_models_committed)

# init mongo db connections
mongo_db.init_app(app)


@app.before_first_request
def set_check_authorized(*args, **kwargs):
    for endpoint in app.url_map._rules_by_endpoint:
        app.view_functions[endpoint] = check_authorized(
            app.view_functions[endpoint])
    for view in admin._views:
        if view.is_visible():
            view.is_visible = partial(is_visible, view)


def is_visible(view):
    is_super_user, admin_user = get_admin_user()
    if is_super_user:
        return view.is_visible

    show = False
    has_permissions = get_permissions(admin_user)
    for url in view._urls:
        to_be_checked = ['%s.%s[%s]' % (view.endpoint, url[1], method) for
                         method in
                         url[2] if
                         method not in ('HEAD', 'OPTIONS')]
        if set(to_be_checked).issubset(has_permissions):
            show = True
    return show


def check_authorized(view_func):
    if not hasattr(view_func, 'im_class'):
        setattr(view_func, 'im_class', None)
    if not hasattr(view_func, 'im_self'):
        setattr(view_func, 'im_self', None)

    @wraps(view_func, assigned=('im_self', 'im_class'))
    def wrapper(*args, **kwargs):
        to_be_checked = '%s[%s]' % (request.endpoint, request.method)
        ignores = ('static[GET]', 'admin_handlers.home[GET]',
                   'admin_handlers.login_view[GET]', 'admin.static[GET]',
                   'admin_handlers.logout_view[GET]'
        )
        if to_be_checked in ignores:
            return view_func(*args, **kwargs)
        referrer = request.referrer or url_for('admin_handlers.home')
        is_super_user, admin_user = get_admin_user()
        if not is_super_user:
            has_permissions = get_permissions(admin_user)
            if 'ROOT' in has_permissions:
                return view_func(*args, **kwargs)
            if to_be_checked not in has_permissions:
                if to_be_checked == 'admin_handlers.home[GET]':
                    return redirect(url_for('admin_handlers.login_view'))
                flash(u'你没有权限哦!', 'error')
                return redirect(referrer)
        return view_func(*args, **kwargs)

    return wrapper


def get_admin_user():
    try:
        logged_user = login.current_user.name
    except:
        abort(403)
    admin_user = admin_session.query(AdminUser).filter_by(
        name=logged_user).first()
    is_super_user = False
    if admin_user:
        is_super_user = admin_session.query(AuthPermission).filter_by(
            name='ROOT').first() in admin_user.permissions
    return is_super_user, admin_user


def get_cache_key(fname):
    try:
        return fname+'_'+login.current_user.name
    except:
        abort(403)


@cache.memoize(make_name=get_cache_key)
def get_permissions(admin_user):
    if not admin_user:
        return []
    group_permissions = []
    if admin_user.group_id is not None:
        group_permissions = list(itertools.chain.from_iterable(
            [group.permissions for group in
             admin_session.query(AuthGroup).filter(
                 AuthGroup.id == admin_user.group_id).all()]))
    has_permissions = [permission.view_name for permission in
                       admin_user.permissions + group_permissions]
    return has_permissions


@app.teardown_appcontext
def shutdown_session(exception=None):
    aux_session.remove()


@app.teardown_appcontext
def teardown_api_session(exception):
    try:
        if exception:
            api_session.rollback()
        else:
            api_session.commit()
    finally:
        api_session.remove()


@app.teardown_appcontext
def teardown_admin_session(exception):
    try:
        if exception:
            admin_session.rollback()
        else:
            admin_session.commit()
    finally:
        admin_session.remove()


@app.errorhandler(403)
def forbidden_403(exception):
    return redirect(url_for('admin_handlers.home'))

# Initialize babel
babel = Babel(app)


@babel.localeselector
def get_locale():
    override = request.args.get('lang')
    if override and override in VALID_LOCALES:
        session['lang'] = override
    return session.get('lang', VALID_LOCALES[0])


login_manager = login.LoginManager()
login_manager.setup_app(app)
# Create user loader function
@login_manager.user_loader
def load_user(user_id):
    return admin_session.query(AdminUser).get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('admin_handlers.home'))


class AnonymousUser(AnonymousUserMixin):
    """AnonymousUser definition"""

    def __init__(self):
        self.roles = ImmutableList()

    def has_role(self, *args):
        """Returns `False`"""
        return False


setup_admin(app)
admin.init_app(app)
application = app
