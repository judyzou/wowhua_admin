from wowhua_admin.views import SafeView


class UserView(SafeView):
    can_edit = True
    can_create = True
    column_default_sort = 'id'
    column_filters = ('mobile', )
    column_searchable_list = ('mobile', )
    column_list = ('id', 'nickname', 'mobile', 'gender', 'birth_date', 'city', 'created')

