from wowhua_admin.views import SafeView


class AdvertView(SafeView):
    can_edit = True
    can_create = True
