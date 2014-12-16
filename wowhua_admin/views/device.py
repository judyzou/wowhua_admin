from wowhua_admin.views import MongoSafeView

class DeviceView(MongoSafeView):
    can_edit = True
    can_create = True
