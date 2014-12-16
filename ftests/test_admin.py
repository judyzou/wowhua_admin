#!/usr/env/bin python
# -*- coding: utf-8 -*-

from functools import partial
import unittest
from mock import Mock
from flask.ext import login
from wowhua_admin import wsgi_application
from wowhua_admin.wsgi_application import application
from wowhua_db.model_utils.data_util import init_dbs, drop_dbs

from wowhua_admin.db_session import api_session
from wowhua_admin.db_session import admin_session

class AdminTestCase(unittest.TestCase):

    def setUp(self):
        app = application
        app.config['TESTING'] = True
        wsgi_application.get_admin_user = lambda: (True, Mock())
        self.app = app.test_client()
        init_dbs()

    def tearDown(self):
        api_session.remove()
        admin_session.remove()
        drop_dbs()

    def test_l10n(self):
        rv = self.app.get('/')
        resp = rv.data
        print resp
        self.assertTrue('欢迎来玩耍' in resp)

        rv = self.app.get('/?lang=en')
        resp = rv.data
        self.assertTrue('Welcome to the Admin,' in resp)

    def test_admin_views_success(self):
        login.current_user = Mock()
        login.current_user.name = 'admin'

        rv = self.app.get('/')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')

        rv = self.app.get('/admin/')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')

        rv = self.app.get('/admin/user/')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')

        rv = self.app.get('/admin/timeline/')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')

    def test_transaction_filters(self):
        rv = self.app.get('/admin/transaction/')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')

        rv = self.app.get('/admin/transaction/?flt1_0=1')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')

        rv = self.app.get('/admin/transaction/?flt0_0=1&flt1_4=2')
        self.assertEquals(rv.status_code, 200)
        self.assertEqual(rv.content_type, 'text/html; charset=utf-8')


if __name__ == "__main__":
    unittest.main()
