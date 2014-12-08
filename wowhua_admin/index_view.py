from flask.ext import login
from flask.ext.admin import AdminIndexView

class AdminIndexViewWithAlarm(AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

