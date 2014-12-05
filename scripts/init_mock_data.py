#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wowhua_db.api.util import scoped_session as api_session
from wowhua_db.aux.util import scoped_session as aux_session

from wowhua_db.api.models import *
from wowhua_db.aux.models import *
from wowhua_db.model_utils.data_util import init_dbs, drop_dbs
from wowhua_db.util import add_order, reject_order
from datetime import datetime
from datetime import timedelta

def insert_data():
    user, wallet = UserMapper.add_user(api_session, device_id='12312312312312',
                                       mobile='2'*11)
    expire_seconds = 10
    advert_play = AdvertMapper()
    advert_play.title = 'open a page'
    advert_play.expired = datetime.now() + timedelta(seconds=expire_seconds)
    advert_play.lock_image_url = 'https://img.wowhua.com/xxxxxx.img'
    advert_play.web_link = 'https://www.taobao.com/a/b/c'
    advert_play.apk_link = 'https://cdn.wowhua.com/download/xxxxx.apk'
    advert_play.download_award = 0.03
    advert_play.play_award = 0.13
    advert_play.left_slide_award = 0.03
    advert_play.right_slide_award = 0.02
    advert_play.end_step = ADVERT_STEPS.play.value
    aux_session.add(advert_play)
    aux_session.commit()
    advert_ctx = AdvertContextMapper.get_obj_create_if_missing(api_session, advert_play, user.id)
    advert_ctx_dict = advert_ctx.to_dict()

    advert_ctx.right_slide(api_session, advert_play)
    advert_ctx_dict = advert_ctx.to_dict()

    advert_ctx.left_slide(api_session, advert_play)
    advert_ctx_dict = advert_ctx.to_dict()

    advert_ctx.download(api_session, advert_play)
    advert_ctx_dict = advert_ctx.to_dict()

    advert_ctx.next_task(api_session, advert_play)
    advert_ctx_dict = advert_ctx.to_dict()

    advert_ctx.next_task(api_session, advert_play)
    advert_ctx_dict = advert_ctx.to_dict()

    advert_play.end_step = ADVERT_STEPS.ever.value
    advert_ctx.reset(advert_play)
    advert_ctx_dict = advert_ctx.to_dict()

    item = ItemMapper(category_id=ITEM_CATEGORY.phone_charge_card.value,
                      title="phone charge card 30 yuan",
                      price=30, stock_num=100, sale_num=100,
                      icon_url="http://cdn.wowhua.com/icon/1",
                      detail_url="http://cms.wowhua.com/detail/1")
    aux_session.add(item)
    aux_session.flush()
    item_dict = item.to_dict()
    assert item_dict['price'] == item.price
    aux_session.commit()

    user, wallet = UserMapper.add_user(api_session, device_id='123123123123213123',
                                       mobile='1'*11)
    wallet.add_registration_income(api_session, 100)


    item = aux_session.query(ItemMapper).get(item_dict['id'])
    order = add_order(api_session, aux_session, user.id, item.id)
    order_dict = order.to_dict()
    assert order_dict['status'] == ORDER_STATUS.request.value
    order.deal('leopold')
    order_dict = order.to_dict()
    assert order_dict['status'] == ORDER_STATUS.dealing.value
    order.approve()
    order_dict = order.to_dict()
    assert order_dict['status'] == ORDER_STATUS.approved.value

    order = add_order(api_session, aux_session, user.id, item.id)
    order.deal('leopold')

    order = reject_order(api_session, aux_session, order.id)
    order_dict = order.to_dict()
    assert order_dict['status'] == ORDER_STATUS.rejected.value

    advert_count = 2 * BOOKMARK_MAX_ROWS
    expire_seconds = 2
    for i in range(advert_count):
        advert_link = AdvertMapper(title='open a page %s' % i,
                             expired=datetime.now() + timedelta(seconds=expire_seconds))
        advert_link.lock_image_url = 'https://img.wowhua.com/xxxxxx%s.img' % i
        advert_link.web_link = 'https://www.taobao.com/a/b/c/%s' % i
        advert_link.left_slide_award = 0.03
        advert_link.right_slide_award = 0.02
        advert_link.end_step = ADVERT_STEPS.left_slide.value
        aux_session.add(advert_link)
    aux_session.commit()

    user, wallet = UserMapper.add_user(api_session, device_id='123123123123213123',
                                       mobile='3'*11)
    adverts = aux_session.query(AdvertMapper).all()
    for advert in adverts:
        bookmark = BookmarkMapper.insert_or_replace_old(api_session, advert, user.id)
        api_session.flush()
    api_session.commit()

    bookmarks = api_session.query(BookmarkMapper).filter(BookmarkMapper.user_id==user.id).all()
    bookmarks_dict = BookmarkMapper.to_dict_list(bookmarks)
    for bm in bookmarks_dict:
        assert bm['advert_id'] > BOOKMARK_MAX_ROWS

if __name__ == '__main__':
    drop_dbs()
    init_dbs()
    insert_data()
