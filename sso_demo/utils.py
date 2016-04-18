#coding:utf-8

import os
import re
import imp
import json
from flask import jsonify


def res_json(code, data, message, success, **kwargs):
    res = jsonify(
        code=code,
        data=data,
        message=message,
        success=success,
        **kwargs
    )
    if str(code) in ["200", "401", "403"]:
        res.status_code = code
    return res