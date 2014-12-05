#!/usr/env/bin python
# -*- coding: utf-8 -*-

import unittest
import datetime
from wowhua_admin.models import Timeline
from wowhua_admin.models import add_timeline
from wowhua_admin.wsgi_application import application
from wowhua_admin.db_session import api_session as scoped_session
from wowhua_db.model_utils.data_util import init_dbs, drop_dbs


class TimelineTestCase(unittest.TestCase):

    def setUp(self):
        app = application
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_dbs()

    def tearDown(self):
        scoped_session.remove()
        drop_dbs()

    def testInsert(self):
        timeline_info = {
            'action': 'insert',
            'action_time': datetime.datetime.now(),
            'admin_user': 'admin',
            'resource': 'Provider',
            'detail': 'test'
        }
        timeline = Timeline(**timeline_info)
        timeline.save()
        new_timeline = Timeline.objects(**timeline_info)[0]
        self.assertEquals(timeline, new_timeline)

    def testAddTimeline(self):
        timeline_info = {
            'action': 'insert',
            'action_time': datetime.datetime.now(),
            'resource': 'Provider',
            'detail': "{'test': True}",
            'admin_user': 'admin_test'
        }
        add_timeline(**timeline_info)
        timeline = Timeline.objects(**timeline_info)[0]
        self.assertTrue(timeline)

