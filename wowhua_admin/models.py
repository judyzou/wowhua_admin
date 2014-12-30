import datetime

from flask.ext import login
from sqlalchemy.orm import mapper, relationship
from wowhua_admin.log import logger

from wowhua_db.admin.models import auth_permission_table
from wowhua_db.admin.models import auth_group_table
from wowhua_db.admin.models import admin_user_table
from wowhua_db.admin.models import auth_group_permission_table
from wowhua_db.admin.models import auth_admin_permission_table
from wowhua_db.api.models import UserMapper as User
from wowhua_db.api.models import TransactionMapper as Transaction
from wowhua_db.api.models import AdvertContextMapper as AdvertContext
from wowhua_db.api.models import BookmarkMapper as Bookmark
from wowhua_db.api.models import WalletMapper as Wallet
from wowhua_db.api.models import OrderMapper as Order
from wowhua_db.api.models import TaskMapper as Task
from wowhua_db.mongo.models import AdvertDocument as Advert
from wowhua_db.mongo.models import ItemDocument as Item
from wowhua_db.mongo.models import DeviceDocument as Device
from wowhua_db.mongo.models import AddressDocument as Address
from wowhua_db.mongo.models import AnnouncementDocument as Announcement
from wowhua_db.mongo.models import BankAccountDocument as BankAccount
from wowhua_db.mongo.models import AlipayAccountDocument as AlipayAccount
from wowhua_db.mongo.models import Document, StringField, DateTimeField


class OperatorLog(Document):
    admin_user = StringField()
    detail = StringField()
    action_time = DateTimeField()


def write_log(detail):
    action_time = datetime.datetime.now()
    admin_user = login.current_user.name
    log_info = {
        'admin_user': admin_user,
        'action_time': action_time,
        'detail': detail
    }
    try:
        operator_log = OperatorLog(**log_info)
        operator_log.save()
    except Exception, e:
        logger.error('Write operator log Error, Error message: %s', str(e),
                     exc_info=True)


class Timeline(Document):
    action_time = DateTimeField()
    action = StringField()
    admin_user = StringField()
    resource = StringField(max_length=200)
    detail = StringField()


def add_timeline(action, resource, detail, admin_user, action_time=None):
    action_time = action_time if action_time else datetime.datetime.now()
    timeline_info = {
        'admin_user': admin_user,
        'action': action,
        'action_time': action_time,
        'resource': resource,
        'detail': detail
    }
    try:
        timeline_info['detail'] = str(detail)
        timeline = Timeline(**timeline_info)
        timeline.save()
    except Exception, e:
        logger.error('Logging timeline Error, Error message: %s', str(e),
                     exc_info=True)
    finally:
        logging_timeline(timeline_info)


def logging_timeline(timeline, error_info=None):
    log_content = ''
    if timeline['action'] in ('login', 'logout', 'register'):
        log_content = '%s %s at %s.' % (timeline['admin_user'],
                                        timeline['action'],
                                        timeline['action_time'])

    else:
        action_dict = {
            'insert': 'inserted',
            'update': 'updated'
        }
        action = action_dict.get(timeline['action'], timeline['action'])
        message = timeline['detail']
        log_content = "%s, %s %s by %s. %s." % (timeline['action_time'],
                                                timeline['resource'],
                                                action,
                                                timeline['admin_user'],
                                                message)
    log_content = 'TimelineLog: %s' % log_content
    logger.info(log_content)


class AuthPermission(object):
    def __init__(self, name=None, view_name=None):
        self.name = name
        self.view_name = view_name

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_or_create_super_permission(admin_session):
        permission = admin_session.query(AuthPermission).filter_by(
            view_name='*').first()
        if permission:
            return permission
        else:
            permission = AuthPermission(name='ROOT', view_name='*')
            admin_session.add(permission)
            admin_session.commit()
            return permission


class AuthGroupPermission(object):
    pass


class AuthGroup(object):
    def __init__(self, name=None):
        self.name = name

    def __unicode__(self):
        return self.name


class AdminPermission(object):
    def __unicode__(self):
        return self.name


class AdminUser(object):
    def __init__(self, name=None):
        assert name != None
        self.name = name

    # Flask-Login integration
    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    def is_superuser(self):
        return False

    # Required for administrative interface
    def __unicode__(self):
        return self.name

    @staticmethod
    def get_or_create_adminuser(admin_session, name):
        # Looks up an object with the given name, creating one if necessary.
        assert name is not None
        assert name != ''
        admin_user = admin_session.query(AdminUser).filter_by(
            name=name).first()
        if admin_user is None:
            admin_user = AdminUser(name=name)
            admin_session.add(admin_user)
            log_data = {
                'action': 'register',
                'resource': 'AdminUser',
                'detail': '',
                'admin_user': admin_user.name
            }
            add_timeline(**log_data)

        admin_session.commit()
        return admin_user

    def add_permission(self, admin_session, permission):
        assert self.name != None
        if self.permissions == None:
            self.permissions = [permission]
        else:
            self.permissions.append(permission)
        admin_session.commit()
        return self.permissions


mapper(AuthPermission, auth_permission_table)
mapper(AuthGroup, auth_group_table, properties={
    'permissions': relationship(AuthPermission, auth_group_permission_table,
                                backref='groups')})
mapper(AdminUser, admin_user_table, properties={
    'groups': relationship(AuthGroup),
    'permissions': relationship(AuthPermission, auth_admin_permission_table,
                                backref='admin_users')
})

