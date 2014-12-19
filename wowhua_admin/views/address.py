from wowhua_admin.views import MongoSafeView


class AddressView(MongoSafeView):
    can_edit = True
    can_create = True