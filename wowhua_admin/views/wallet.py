from wowhua_admin.views import SafeView


class WalletView(SafeView):
    can_edit = True
    can_create = True
    column_filters = ('user_id', )

    column_list = ('user_id', 'balance', 'total_income', 'task_income', 'right_slide_income',
                   'left_slide_income', 'registration_income', 'invite_income',
                   'activity_income')
