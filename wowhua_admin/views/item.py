from wowhua_admin.views import MongoSafeView


class ItemView(MongoSafeView):
    can_edit = True
    can_create = True
