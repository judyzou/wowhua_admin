from wowhua_admin.views import MongoSafeView


class BankAccountView(MongoSafeView):
    can_edit = True
    can_create = True
