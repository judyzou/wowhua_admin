from wowhua_admin.views import MongoSafeView


class AlipayAccountView(MongoSafeView):
    can_edit = True
    can_create = True

