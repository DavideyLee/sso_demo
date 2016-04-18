# coding=utf-8

import re
import hmac
import time
import traceback
import requests
from utils import res_json
from functools import wraps
from flask.ext.babel import gettext as _
from flask import g, session, redirect, current_app, request, render_template, jsonify

__author__ = 'Feng Lu'

token_re = re.compile(r"\??\b_token=\w+&?")


class PermissionDeniedException(Exception):
    def __init__(self, permissions):
        super(Exception, self).__init__(_('permissions %(perm)s required', perm=' or '.join(permissions)))


class Auth(object):
    @classmethod
    def required(cls, permissions, error_resp_type="json"):
        if not (isinstance(permissions, list) or isinstance(permissions, tuple)):
            permissions = [permissions, ]

        if "super.admin" not in permissions:
            permissions.append("super.admin")

        admin_perms = set(map(lambda x: '{0}.admin'.format('.'.join(x.split('.')[:-1])), permissions))
        permissions = list(set(permissions) | admin_perms)

        def wrap(func):
            @wraps(func)
            def inner_wrap(*args, **kwargs):
                if hasattr(g, 'user'):
                    if any(map(lambda x: x in permissions, g.user['permissions'])):
                        return func(*args, **kwargs)
                if len(permissions) == 0:
                    return func(*args, **kwargs)
                msg = u"没有权限访问"
                if error_resp_type == "json":
                    return res_json(**{"code": 403, "data": "", "message": unicode(msg), "success": False})
                elif error_resp_type == "html":
                    return render_template("common/fail.html", message=msg)
                else:
                    return res_json(**{"code": 403, "data": "", "message": unicode(msg), "success": False})
            return inner_wrap
        return wrap

    @classmethod
    def allow(cls, permissions):
        if not (isinstance(permissions, list) or isinstance(permissions, tuple)):
            permissions = [permissions, ]
        if "super.admin" not in permissions:
            permissions.append("super.admin")

        admin_perms = set(map(lambda x: '{0}.admin'.format('.'.join(x.split('.')[:-1])), permissions))
        permissions = list(set(permissions) | admin_perms)

        if not hasattr(g, 'user'):
            return False
        if any(map(lambda x: x in permissions, g.user['permissions'])) or len(permissions) == 0:
            return True
        return False

    @classmethod
    def load_user(cls):
        if not current_app.config.get('SSO_ENABLE'):
            g.user = current_app.config.get("LOCAL_USER")
            return
        if request.values.get("_token"):
            session["user_token"] = request.values.get("_token")
        if session.get('user_token'):
            url = '%s/account/user_info.json?token=%s&secret=%s&app=%d' % (
                current_app.config.get('SSO_URL'),
                session.get('user_token'),
                current_app.config.get('SSO_APP_SECRET'),
                current_app.config.get('SSO_APP_ID')
            )
            try:
                req = requests.get(url)
                resp = req.json()
                if resp['code'] == 200:
                    g.user = resp["data"]
                    if token_re.findall(request.url):
                        return redirect(token_re.sub("", request.url))
                elif resp['code'] == 403:
                    return render_template("include/fail.html", message=resp["message"])
                else:
                    return redirect('%s/account/login?redirect=%s' % (
                        current_app.config.get('SSO_URL'), token_re.sub("", request.url)))
            except Exception, e:
                return redirect('%s/account/login?redirect=%s' % (
                    current_app.config.get('SSO_URL'), token_re.sub("", request.url)))
        else:
            return redirect('%s/account/login?redirect=%s' % (
                current_app.config.get('SSO_URL'), token_re.sub("", request.url)))

    @classmethod
    def load_api(cls):
        """
        import hmac
        secretId = "b10041ab27f7408696efe138e2bd53ae"
        secretKey = "22YH8cD2knk2skFyFWb2ndS2FSB5YNmb3kiHBWQWGxZTNmHDPwP5iEJJFSsaWBz8"
        signature = hmac.new(secretKey, secretId).hexdigest()
        headers = {
            "x-secretid": secretId,
            "x-signature": signature
        }
        res = post('xxxxxx', headers=headers, data=xxxxxx)

        curl "http://172.19.17.36:8002/passport/api/v1/foo.json?x-signature=ee36f1e44ce19c9e25c90d50ef1d7a2f&x-secretid=jhdimn27qgbbgxmr"

        curl "http://172.19.17.36:8002/passport/api/v1/foo.json" \
        -H "x-signature:ee36f1e44ce19c9e25c90d50ef1d7a2f" -H "x-secretid:jhdimn27qgbbgxmr"
        """
        if not current_app.config.get('SSO_ENABLE'):
            g.user = current_app.config.get("LOCAL_USER")
            return
        # 必须要提供三个头参数
        secretid = request.headers.get("x-secretid") or request.values.get("x-secretid")
        signature = request.headers.get("x-signature") or request.values.get("x-signature")
        if secretid and signature:
            url = '%s/account/check_secret.json' % current_app.config.get('SSO_URL')
            body = {
                "secretId": secretid,
                "signature": signature,
                "appSecret": current_app.config.get('SSO_APP_SECRET'),
                "appId": current_app.config.get('SSO_APP_ID')
            }
            try:
                req = requests.post(url, body)
                resp = req.json()
                if resp['status'] == 200:
                    secret = resp["secret"]
                    # 生成签名
                    serv_signature = hmac.new(str(secret["key"]), str(secretid)).hexdigest()
                    if serv_signature != signature:
                        return jsonify({"retcode": -1, "msg": "x-signature is incrrect! ", "result": "", "type": "str"})
                    g.user = resp["data"]
                    if token_re.findall(request.url):
                        return redirect(token_re.sub("", request.url))
                else:
                    return jsonify({"retcode": -1, "msg": resp.get("message"), "result": "", "type": "str"})
            except Exception, e:
                current_app.logger.error(traceback.format_exc())
                return jsonify({"retcode": -1, "msg": e.message, "result": "", "type": "str"})
        else:
            return jsonify(
                {"retcode": -1, "msg": "x-secretid and x-signature in headers or query_string is required", "result": "",
                 "type": "str"})
