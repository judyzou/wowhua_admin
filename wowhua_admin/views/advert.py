from wowhua_admin.views import MongoSafeView


class AdvertView(MongoSafeView):
    can_edit = True
    can_create = True
