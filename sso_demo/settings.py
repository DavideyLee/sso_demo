# coding=utf-8

import sys
import logging
from .filters import FILTERS
from .extend import EXTENDS
from flask.ext.babel import Babel
from flask import Flask, request

__author__ = 'Feng Lu'


APP_NAME = "sso_demo"


def create_app(conf=None):
    app = Flask(APP_NAME)
    if conf:
        app.config.from_object(conf)

    configure_extensions(app)
    configure_filters(app)
    return app


def configure_extensions(app):
    app.jinja_options['extensions'].append('jinja2.ext.do')
    for ex in EXTENDS:
        app.jinja_env.globals[ex[0]] = ex[1]


def configure_blueprints(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)
    return app


def configure_filters(app):
    for ft in FILTERS:
        app.jinja_env.filters[ft[0]] = ft[1]


