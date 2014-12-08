from flask.ext.script import Manager
from flask import url_for

from wowhua_admin.db_session import admin_session
from wowhua_admin.wsgi_application import application as app
from wowhua_db.model_utils.data_util import drop_dbs, init_dbs
from wowhua_admin.models import AuthGroup, AuthPermission, AdminUser

manager = Manager(app)

@manager.command
def reset_db():
    drop_dbs()
    init_dbs()


@manager.command
def reset_permission():
    all_urls = app.url_map._rules_by_endpoint
    ignors = ('ajax_lookup', 'static', 'action_view')
    existing_endpoint = admin_session.query(AuthPermission).all()
    root_group = admin_session.query(AuthGroup).filter_by(name='ROOT').first()
    if not root_group:
        root_group = AuthGroup('ROOT')
        admin_session.add(root_group)

    for url, rule in all_urls.items():
        view_class = app.view_functions[url]
        can_edit = None
        can_delete = None
        can_create = None
        if hasattr(view_class, 'im_self'):
            can_delete = getattr(view_class.im_self, 'can_delete', None)
            can_edit = getattr(view_class.im_self, 'can_edit', None)
            can_create = getattr(view_class.im_self, 'can_create', None)

        if url.find('.') >= 0:
            view, endpoint = url.split('.')
        else:
            endpoint = url

        if endpoint == 'delete_view' and can_delete is False:
            continue
        if endpoint == 'edit_view' and can_edit is False:
            continue
        if endpoint == 'create_view' and can_create is False:
            continue

        methods = ['%s[%s]' % (url, method) for
                   method in
                   rule[0].methods if
                   method not in ('HEAD', 'OPTIONS') and
                   '%s[%s]' % (url, method) not in existing_endpoint and
                   endpoint not in ignors]
        for method in methods:
            permission = admin_session.query(AuthPermission).filter_by(view_name=method).first()
            if not permission:
                permission = AuthPermission(method, method)
                admin_session.add(permission)
            if method not in root_group.permissions:
                root_group.permissions.append(permission)

        all_users = admin_session.query(AdminUser).all()
        for admin_user in all_users:
            admin_user.groups = root_group
    admin_session.commit()

if __name__ == "__main__":
    manager.run()
