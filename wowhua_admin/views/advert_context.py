from wowhua_admin.views import SafeView


class AdvertContextView(SafeView):
    can_edit = True
    can_create = True
    column_filters = ('advert_id', 'user_id', 'current_step', 'closed')
    column_list = ('user_id', 'advert_id', 'advert_category', 'current_step', 'left_slide_award',
                   'right_slide_award', 'download_award', 'play_award',
                   'closed', 'expired', 'created')
