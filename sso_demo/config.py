#coding:utf-8

import os
from flask.ext.babel import gettext as _

__author__ = 'Feng Lu'


class Config(object):
    APPNAME = "sso_demo"


class ProductionConfig(Config):
    SECRET_KEY = "dddwerewgwsdsg"
    SSO_URL = "http://172.19.50.1"
    SSO_APP_SECRET = "xxsdfwerwerwf"
    SSO_APP_ID = 10
    SSO_ENABLE = True


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "yiwerwerwfdwsdsf"
    SSO_URL = "http://127.0.0.1:8005"
    SSO_APP_SECRET = "pwFdm28hNtmNstGx"
    SSO_APP_ID = 9
    SSO_ENABLE = True
