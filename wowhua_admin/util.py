# -*- coding: utf-8 -*-
from email.mime.text import MIMEText

import re
import signal
import logging
import smtplib
import jinja2
import urlparse
from flask import url_for, request, Markup
from flask.ext import login
from flask.ext.babelex import lazy_gettext as _
from wtforms.widgets.core import HTMLString
from wowhua_admin.log import logger

from wowhua_admin.models import add_timeline
from wowhua_admin.models import User
from wowhua_admin.db_session import api_session
from wowhua_admin.db_session import admin_session


def setupShutDownSignal(signal_owner, shutdown):
    if signal.getsignal(signal.SIGINT) == signal.default_int_handler:
        # only handle if there isn't already a handler, e.g. for Pdb.
        signal_owner.signal(signal.SIGINT, shutdown)
    signal_owner.signal(signal.SIGCHLD, shutdown)
    signal_owner.signal(signal.SIGTERM, shutdown)


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def get_full_url(path='admin_handlers.home'):
    # scheme = request.headers.get('X-Forwarded-Proto')
    service_url = urlparse.urljoin(request.url_root, url_for(path))
    # service_url.replace('http://', "%s://" % scheme)
    return service_url


def user_id_formatter(user_id):
    if user_id and user_id != 'None':
        user = api_session.query(User).get(user_id)
        if user:
            filter_url = '%s?flt1_8=%s' % (
                url_for('user.index_view'), user_id)
            return Markup(u"<a href='%s'>%s</a>" % (filter_url, user.name))
    return user_id


def time_formatter(datetime_str):
    if datetime_str:
        try:
            return datetime_str.strftime("%Y-%m-%d %H:%M:%S")
        except:
            logger.error('formatting datetime %s error.' % datetime_str, )
    return ""


def permissions_formatter(view, context, model, name):
    return u'，'.join([permission.name for permission in model.permissions if
                      permission.name != 'ROOT'])


def common_formatter(string):
    if string == 'None' or string is None:
        return _('None')
    else:
        return string


jinja2.filters.FILTERS['time_formatter'] = time_formatter
jinja2.filters.FILTERS['common_formatter'] = common_formatter


def is_accessible(self):
    return login.current_user.is_authenticated()


def is_column_equal(old_value, new_value):
    empty_values = [0, '0', '', False, None, 'False', 'None']
    if old_value in empty_values:
        old_value = None
    if new_value in empty_values:
        new_value = None
    return old_value == new_value


def on_models_committed(sender, changes):
    admin_user = getattr(login.current_user, 'name', None)
    if not admin_user:
        return

    for table, old_values, new_values, change in changes:
        detail = {}
        for column in table.columns:
            key = column.name
            new_value = new_values.get(key, None)
            if change == 'update':
                old_value = old_values.get(key, None)
                if not is_column_equal(old_value, new_value):
                    detail[key] = {'old': old_value, 'new': new_value}
            elif change in ('insert', 'delete'):
                detail[key] = new_value
        log_data = {
            'action': change,
            'resource': str(table),
            'detail': detail,
            'admin_user': admin_user
        }
        if change in ('insert', 'update') and not detail:
            return
        add_timeline(**log_data)


class ReadonlyInput(object):
    def __call__(self, field):
        return HTMLString(
            u'<input type="text" name="%s" value="%s" readonly />' % (
                field.name + '_', field.data))
