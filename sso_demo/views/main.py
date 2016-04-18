# coding=utf-8

import json
import traceback
from ..auth import Auth
from flask import Blueprint, render_template, redirect, session, current_app, request, g


__author__ = 'Feng Lu'


main = Blueprint('main', __name__)
main.before_request(Auth.load_user)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/foo/list")
@Auth.required("foo.list")
def foo_list():
    return "foo.list"


@main.route("/foo/user")
def foo_user():
    return json.dumps(g.user, indent=4)


@main.route("/foo/view")
@Auth.required("foo.view", error_resp_type="html")
def foo_view():
    return "foo.view"


@main.route("/foo/get")
def foo_get():
    if Auth.allow("foo.list"):
        msg = "you can get..."
    else:
        msg = "you can not get!"
    return msg


@main.route("/logout")
def logout():
    session.clear()
    return redirect('%s/account/logout?redirect=%s' % (current_app.config.get('SSO_URL'), request.referrer))