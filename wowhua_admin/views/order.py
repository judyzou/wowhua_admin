from wowhua_admin.views import SafeView


class OrderView(SafeView):
    can_edit = True
    can_create = True
    column_list = ('user_id', 'item_id', 'status', 'trans_id', 'created', 'dealing_time',
                   'handled_time', 'cancel_trans_id', 'commnet', 'admin_user')
