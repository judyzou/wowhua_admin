#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.admin import Admin
from flask.ext.mongoengine import MongoEngine
from flask.ext.babelex import lazy_gettext as _
from wowhua_admin.index_view import AdminIndexViewWithAlarm


admin = Admin(name=_(u'Admin'),
              index_view=AdminIndexViewWithAlarm(name=_('Home')))
db = MongoEngine()
