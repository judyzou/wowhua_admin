from wowhua_admin.views import MongoSafeView


class AnnouncementView(MongoSafeView):
    can_edit = True
    can_create = True
