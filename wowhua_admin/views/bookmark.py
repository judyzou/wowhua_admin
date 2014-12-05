from wowhua_admin.views import SafeView


class BookmarkView(SafeView):
    can_edit = True
    can_create = True
