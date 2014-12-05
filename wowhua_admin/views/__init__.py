# -*- coding: utf-8 -*-

import urlparse
from pycas import pycas
from urllib import urlencode
from flask.ext import login
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.mongoengine import ModelView as MongoModelView
from flask.ext.admin import expose, BaseView
from flask.ext.admin import AdminIndexView
from flask.ext.babelex import lazy_gettext as _
from flask import Blueprint, Markup, url_for, redirect, render_template, request
from wowhua_admin import cache

from wowhua_admin.util import time_formatter
from wowhua_admin.config import get_config
from wowhua_admin.util import get_full_url
from wowhua_admin.models import add_timeline
from wowhua_admin.models import AdminUser
from wowhua_admin.db_session import api_session, admin_session


admin_handlers = Blueprint("admin_handlers", __name__)
setting = get_config()


@admin_handlers.route('/')
def home():
    return render_template('home.html', user=login.current_user)


@admin_handlers.route('/login/', methods=('GET',))
def login_view():
    path = request.args.get('next_page', 'admin_handlers.home')
    ticket = ''
    cas_server = setting['cas_server']
    status = 0
    cas_login = ''
    admin_user = None

    ticket = request.args.get('ticket', '')
    if ticket:
        next_page = get_full_url(path=path)
        status, uname = pycas.validate_cas_1(cas_server, next_page, ticket)
        admin_user = AdminUser.get_or_create_adminuser(admin_session, uname)
        login.login_user(admin_user)
    else:
        service_url = get_full_url(path='admin_handlers.login_view')
        status, cas_login, another = pycas.login(cas_server, service_url)

    if status != 0 or not admin_user:
        return redirect(cas_login)
    else:
        log_data = {
            'action': 'login',
            'resource': 'AdminUser',
            'detail': '',
            'admin_user': admin_user.name
        }
        add_timeline(**log_data)
        return redirect(next_page)


@admin_handlers.route('/logout/')
def logout_view():
    next_path = request.args.get('next_page', 'admin_handlers.home')
    logout_url = urlparse.urljoin(setting['cas_server'], 'logout')
    next_page = get_full_url(path=next_path)
    logout_url += '?' + urlencode({'url': next_page})
    admin_user = login.current_user

    log_data = {
        'action': 'logout',
        'resource': 'AdminUser',
        'detail': '',
        'admin_user': admin_user.name
    }
    add_timeline(**log_data)
    cache_key = u'wowhua_admin.wsgi_application.get_permissions_' + login.current_user.name
    cache.cache.delete(cache_key)
    login.logout_user()
    return redirect(logout_url)


@admin_handlers.errorhandler(403)
def forbidden_403(exception):
    return redirect(url_for('admin_handlers.home'))


class SafeView(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    page_size = 20
    column_labels = {}
    list_template = 'model/list.html'
    edit_template = 'model/edit.html'
    create_template = 'model/create.html'
    column_filters = ('id',)

    def _edit(view, context, model, name):
        edit_url = '%s/edit?id=%s' % (view.url, str(model.id))
        if name in ('id', 'name'):
            return Markup("<a href='%s'>%s</a>" % (edit_url, getattr(model, name)))

    column_formatters = {
        'id': _edit,
        'name': _edit,
    }

    @staticmethod
    def _time_formatter(view, context, model, name):
        datetime_str = getattr(model, name)
        return time_formatter(datetime_str)

    def is_accessible(self):
        return login.current_user.is_authenticated()


class MongoSafeView(MongoModelView):
    can_create = False
    can_edit = False
    can_delete = False
    list_template = 'model/list.html'

    def is_accessible(self):
        return login.current_user.is_authenticated()

    @staticmethod
    def _time_formatter(view, context, model, name):
        datetime_str = getattr(model, name)
        return time_formatter(datetime_str)


class CustomSafeView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

# Create customized index view class
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

    @expose('/')
    def index(self):
        return self.render('index.html')


