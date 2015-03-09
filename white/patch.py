#!/usr/bin/env python
# 2015 Copyright (C) White
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import date, datetime, time
import decimal
import flask
from flask._compat import text_type
from flask.json import JSONEncoder as _JSONEncoder, dumps
from flask import Flask, json, current_app, request


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__') and callable(o.__json__):
            return o.__json__()
        if isinstance(o, (date,
                          datetime,
                          time)):
            return o.isoformat()[:19].replace('T', ' ')
        elif isinstance(o, (int, long)):
            return int(o)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif hasattr(o, '__html__'):
            return text_type(o.__html__())
        return _JSONEncoder.default(self, o)

def jsonify(value):
    """Creates a :class:`~flask.Response` with the JSON representation of
    the given arguments with an `application/json` mimetype.  The arguments
    to this function are the same as to the :class:`dict` constructor.

    Example usage::

        from flask import jsonify

        class User(object):
            def __json__(self):
                return dict(username=g.user.username,
                           email=g.user.email,
                           id=g.user.id)

        @app.route('/_get_current_user')
        def get_current_user():
            return jsonify(user)

    This will send a JSON response like this to the browser::

        {
            "username": "admin",
            "email": "admin@localhost",
            "id": 42
        }

    For security reasons only objects are supported toplevel.  For more
    information about this, have a look at :ref:`json-security`.

    This function's response will be pretty printed if it was not requested
    with ``X-Requested-With: XMLHttpRequest`` to simplify debugging unless
    the ``JSONIFY_PRETTYPRINT_REGULAR`` config parameter is set to false.

    """
    indent = None
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] \
        and not request.is_xhr:
        indent = 2
    return current_app.response_class(dumps(value ,
        indent=indent),
        mimetype='application/json')

def patch_flask():
    flask.json.jsonify = jsonify
    flask.jsonify = flask.json.jsonify
    Flask.json_encoder = JSONEncoder
