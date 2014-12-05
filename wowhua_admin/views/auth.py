# -*- coding: utf-8 -*-

from sqlalchemy import func
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.form import Select2Field
from flask_babelex import lazy_gettext as _

from wowhua_admin.db_session import admin_session
from wowhua_admin.models import AuthPermission
from wowhua_admin.util import permissions_formatter


def get_endpoint_choices(app, get_exsiting=True, keep=None):
    all_urls = app.url_map._rules_by_endpoint
    endpoint_choices = []
    existing_endpoint = []
    if get_exsiting:
        existing_endpoint = [end_point[0] for end_point in admin_session.query(
            AuthPermission.view_name).all()]
        if keep and keep in existing_endpoint:
            existing_endpoint.remove(keep)

    ignors = ('ajax_lookup', 'static')
    for end_point, rule in all_urls.items():
        view_class = app.view_functions[end_point]
        view_name = ''
        can_edit = None
        can_delete = None
        can_create = None
        if view_class.im_self:
            view_name = unicode(view_class.im_self.name) + '.'
            can_delete = getattr(view_class.im_self, 'can_delete', None)
            can_edit = getattr(view_class.im_self, 'can_edit', None)
            can_create = getattr(view_class.im_self, 'can_create', None)

        if end_point.find('.') >= 0:
            view, url_point = end_point.split('.')
        else:
            url_point = end_point

        if url_point == 'delete_view' and can_delete is False:
            continue
        if url_point == 'edit_view' and can_edit is False:
            continue
        if url_point == 'create_view' and can_create is False:
            continue

        methods = [('%s[%s]' % (end_point, method),
                    '(%s)%s%s[%s]' % (view, view_name, url_point, method)) for
                   method in
                   rule[0].methods if
                   method not in ('HEAD', 'OPTIONS') and
                   '%s[%s]' % (end_point, method) not in existing_endpoint and
                   url_point not in ignors]
        endpoint_choices += methods
        endpoint_choices.sort()
    return endpoint_choices


class AuthPermissionView(ModelView):
    column_list = ('id', 'name', 'view_name')
    form_columns = ('name', 'view_name', )
    form_extra_fields = {'view_name': Select2Field(_('View Name'))}
    form_widget_args = {
        'view_name': {
            'style': 'width:500px',
        }
    }
    column_labels = {'name': _('Name'),
                     'id': _('ID'),
                     'permissions': _('Permissions'),
                     'view_name': _('View Name')}

    def get_query(self):
        return self.session.query(self.model).filter(self.model.name != 'ROOT')

    def get_count_query(self):
        return self.session.query(func.count('id')).select_from(
            self.model).filter(self.model.name != 'ROOT')

    def create_form(self, obj=None):
        form_class = super(AuthPermissionView, self).create_form()
        form_class.view_name.choices = get_endpoint_choices(self.admin.app,
                                                            True)
        return form_class

    def edit_form(self, obj=None):
        form_class = super(AuthPermissionView, self).edit_form()
        if not form_class.name.data:
            form_class.name.data = obj.name
        form_class.view_name.choices = get_endpoint_choices(self.admin.app,
                                                            True,
                                                            obj.view_name)
        if not form_class.name.data:
            form_class.view_name.data = obj.view_name
        return form_class


class AuthGroupView(ModelView):
    can_delete = False
    column_list = ('id', 'name', 'permissions')
    create_template = 'model/create_permission.html'
    edit_template = 'model/edit_permission.html'
    column_formatters = {'permissions': permissions_formatter}
    column_labels = {'name': _('Name'),
                     'id': _('ID'),
                     'permissions': _('Permissions')}


class AdminUserView(ModelView):
    can_delete = False
    can_create = False
    column_list = ('id', 'groups', 'name', 'permissions')
    form_columns = ('name', 'permissions', 'groups')
    create_template = 'model/create_permission.html'
    edit_template = 'model/edit_permission.html'
    column_formatters = {'permissions': permissions_formatter}
    column_labels = {'name': _('Name'),
                     'id': _('ID'),
                     'permissions': _('Permissions'),
                     'groups': _('Group')}
