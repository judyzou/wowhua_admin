from wowhua_admin.views import SafeView


class UserView(SafeView):
    can_edit = True
    can_create = True
    column_default_sort = 'id'
    column_filters = ('mobile', 'device_id')
    column_searchable_list = ('mobile', 'device_id')
    column_list = ('mobile', 'device_id', 'gender', 'birth_year', 'created')



