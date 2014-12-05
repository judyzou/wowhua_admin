from wowhua_admin.views import SafeView


class ItemView(SafeView):
    can_edit = True
    can_create = True
