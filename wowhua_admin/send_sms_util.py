# -*- coding:utf=8 -*-

SMS_API_URL = 'http://si.800617.com:4400/SendSms.aspx'
SMS_USER_ID = 'bjzch-1'
SMS_PWD = 'aa5ded'

MOBILE_RE = '^(1(([35][0-9])|(47)|[8][012356789]))\d{8}$'
import urllib2
import urllib
import re

from zch_logger import setup, Logger

env = setup()
env.push_application()
logger = Logger('wowhua_admin.send_sms_utils')


def _send_single_sms(mobile, msg):
    assert msg.decode('GB2312')
    assert len(msg.decode('GB2312')) <= 64
    assert re.match(MOBILE_RE, mobile)

    data = urllib.urlencode({
        'un': SMS_USER_ID,
        'pwd': SMS_PWD,
        'mobile': mobile,
        'msg': msg,
    })
    ret = urllib2.urlopen(SMS_API_URL, data)
    resp = ret.read()
    if resp != 'result=1&':
        logger.error('send sms error: resp = {}, mobile = {}, msg = {}',
                     resp, mobile, msg.decode('GB2312'))
        return 'error'
    else:
        return 'ok'


def send_sms(mobile, msg):
    send_msg = msg
    while len(send_msg) > 64:
        _msg = send_msg[:64].encode('GB2312')
        send_msg = send_msg[64:]
        resp = _send_single_sms(mobile, _msg)
        if resp != 'ok':
            return resp

    resp = _send_single_sms(mobile, send_msg.encode('GB2312'))
    return resp


def mass_send_sms(mobile_list, msg):
    if type(mobile_list) != list:
        logger.error('mobile_list should be list mobile_list = {}',
                     mobile_list)
        return 'error'

    bad_resp = dict()
    for mobile in mobile_list:
        if re.match(MOBILE_RE, mobile):
            resp = send_sms(mobile, msg)
            if resp != 'ok':
                bad_resp[mobile] = resp
        else:
            logger.error('invalid mobile num:{}', mobile)

    if bad_resp == dict():
        return 'ok'
    else:
        return 'error:' + str(bad_resp)


