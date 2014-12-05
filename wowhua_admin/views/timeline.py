# -*- coding: utf-8 -*-

from wowhua_admin.views import MongoSafeView
from flask.ext.babelex import lazy_gettext as _


class OperatorLogView(MongoSafeView):
    column_filters = ('admin_user',)
    column_default_sort = ('action_time', True)
    column_searchable_list = ('admin_user', 'detail')
    column_labels = dict(admin_user=_('Admin User'),
                         action_time=_('Action Time'),
                         detail=_('Detail'),)

    column_formatters = dict(
        action_time=MongoSafeView._time_formatter,
    )


class TimelineView(MongoSafeView):
    column_filters = ('action', 'resource', 'admin_user')
    column_default_sort = ('action_time', True)
    column_searchable_list = ('action', 'resource', 'admin_user')
    column_labels = dict(admin_user=_('Admin User'),
                         action_time=_('Action Time'),
                         action=_('Action'),
                         resource=_('Resource'),
                         detail=_('Detail'),)

    column_formatters = dict(
        action_time=MongoSafeView._time_formatter,
    )

