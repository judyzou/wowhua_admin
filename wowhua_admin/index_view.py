from flask.ext import login
from flask.ext.admin import expose
from flask.ext.admin import AdminIndexView
from wowhua_admin.config import get_config

class AdminIndexViewWithAlarm(AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

