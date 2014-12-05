from wowhua_admin.views import SafeView


class TaskView(SafeView):
    can_edit = True
    can_create = True
