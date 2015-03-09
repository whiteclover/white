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

import hmac
from hashlib import sha1
import base64
import uuid

from functools import wraps

from white.orm import Backend
from white.model import User
from flask import g, session, request, abort, redirect, url_for, current_app, render_template


_guest = User('guest', 'email', 'Guest', 'password', 'bio', 'active', 'guest', uid=0)

def security(role=None):
    def decorator(f):
        @wraps(f)
        def _decorator(*args, **kw):
            me = g.user
            if me.is_guest() and request.path !='admin/login':
                return redirect(url_for('admin.login'))
            access = False 
            if me.is_root():
                access = True
            elif not me.inactive() and (me.is_admin() or me.role == role):
                access = True
                
            if access:
                return f(*args, **kw)
            else:
                return render_template('admin/403.html')
        return _decorator
    return decorator


def init_user():
    """Load user if the auth session validates."""
    try:
        user = _guest
        if 'auth' in session:
            uid = session['auth']
            user = Backend('user').find(uid)
    except:
        user = _guest
    g.user = user


@wraps
def csrf_protect(f):
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

    return f

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = _secert_signature(current_app.config['CSRF_SECRET'], str(uuid.uuid4()))
    return session['_csrf_token']


def _secert_signature(secret, *parts):
    hash = hmac.new(secret, digestmod=sha1)
    for part in parts:
        hash.update(part)
    return hash.hexdigest()