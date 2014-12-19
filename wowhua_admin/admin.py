#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.babelex import lazy_gettext as _

from wowhua_admin.models import OperatorLog
from wowhua_admin.models import AuthPermission
from wowhua_admin.models import AuthGroup
from wowhua_admin.models import AdminUser
from wowhua_admin.models import Timeline
from wowhua_admin.models import Address
from wowhua_admin.models import Device
from wowhua_admin.models import Transaction
from wowhua_admin.models import User
from wowhua_admin.models import Wallet
from wowhua_admin.models import Advert
from wowhua_admin.models import AdvertContext
from wowhua_admin.models import Bookmark
from wowhua_admin.models import Item
from wowhua_admin.models import Order
from wowhua_admin.models import Task
from wowhua_admin.views.auth import AuthPermissionView
from wowhua_admin.views.auth import AuthGroupView
from wowhua_admin.views.auth import AdminUserView
from wowhua_admin.views.timeline import TimelineView, OperatorLogView
from wowhua_admin.views.transaction import TransactionView
from wowhua_admin.views.advert import AdvertView
from wowhua_admin.views.advert_context import AdvertContextView
from wowhua_admin.views.bookmark import BookmarkView
from wowhua_admin.views.item import ItemView
from wowhua_admin.views.order import OrderView
from wowhua_admin.views.user import UserView
from wowhua_admin.views.wallet import WalletView
from wowhua_admin.views.task import TaskView
from wowhua_admin.views.device import DeviceView
from wowhua_admin.views.address import AddressView

from wowhua_admin.db_session import admin_session
from wowhua_admin.db_session import api_session
from wowhua_admin.extensions import admin


def setup_admin(app):
    auth_tran = _('Auth')
    admin.add_view(AuthPermissionView(AuthPermission, admin_session,
                                      name=_('AuthPermission'),
                                      endpoint='authpermission',
                                      category=auth_tran))
    admin.add_view(AuthGroupView(AuthGroup, admin_session, name=_('AuthGroup'),
                                 endpoint='authgroup', category=auth_tran))
    admin.add_view(AdminUserView(AdminUser, admin_session, name=_('AdminUser'),
                                 endpoint='adminuser', category=auth_tran))

    admin.add_view(UserView(User, api_session, name=_('user'), endpoint='user'))
    admin.add_view(WalletView(Wallet, api_session, name=_('wallet'), endpoint='wallet'))
    admin.add_view(BookmarkView(Bookmark, api_session, name=_('bookmark'), endpoint='bookmark'))
    admin.add_view(TaskView(Task, api_session, name=_('task'), endpoint='task'))
    admin.add_view(OrderView(Order, api_session, name=_('order'), endpoint='order'))
    admin.add_view(AdvertContextView(AdvertContext, api_session, name=_('advert_context'), endpoint='advert_context'))
    admin.add_view(TransactionView(Transaction, api_session, name=_('transaction'), endpoint='transaction'))

    admin.add_view(AdvertView(Advert, name=_('advert'), endpoint='advert'))
    admin.add_view(ItemView(Item, name=_('item'), endpoint='item'))
    admin.add_view(DeviceView(Device, name=_('device'), endpoint='device'))
    admin.add_view(AddressView(Address, name=_('address'), endpoint='address'))
    admin.add_view(TimelineView(Timeline, name=_('timeline'), endpoint='timeline'))
    admin.add_view(OperatorLogView(OperatorLog, name=_('Operator Log'), endpoint='operatorlog'))

