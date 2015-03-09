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


from flask import g, request, flash, current_app
from flask import render_template, redirect, url_for, jsonify
from flask import session

from white.controller import admin as bp, ADMIN, EDITOR
from white.security import security

from white.orm import Backend
from white.model import User
from white.domain.user import UserService
from white.flash import flash
from white.lang import text

user_service = UserService()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if g.user.is_guest():
            return render_template('admin/user/login.html')
        return redirect(url_for('admin.post_page'))

    reqp = request.form
    username = reqp.get('username')
    password = reqp.get('password')

    result = user_service.auth(username, password)
    if result['status'] == 200:
        user_service.login(result['user'])
        return redirect(url_for('admin.post_page'))

    flash(text('user.login_error'), 'error')
    return redirect(url_for('admin.login'))


@bp.route('/logout', methods=['GET'])
def logout():
    user_service.logout()
    return redirect(url_for('admin.login'))


@bp.route('/user.json')
def user_json():
    return jsonify(g.user)


@bp.route('/user')
@bp.route('/user/<int:page>')
def user_page(page=1):
    page = user_service.page(page, 5)
    return render_template('admin/user/index.html', users=page)


@bp.route('/user/add', methods=['GET', 'POST'])
@security(ADMIN)
def user_add():
    if request.method == 'GET':
        return render_template('admin/user/add.html', statuses=User.STATUSES, roles=User.ROLES)

    p = request.form.get
    username = p('username')
    email = p('email')
    real_name = p('real_name')
    password = p('password')
    bio = p('bio')
    status = p('status', default='inactive')
    role = p('role', default='user')

    result = user_service.add_user(
        username, email, real_name, password, bio, status, role)
    if result['status'] == 'ok':
        return redirect(url_for('admin.user_edit', uid=result['user'].uid))
    else:
        flash(result['errors'], 'error')
        return render_template('admin/user/add.html', statuses=User.STATUSES, roles=User.ROLES)


@bp.route('/user/<int:uid>/edit', methods=['GET', 'POST'])
def user_edit(uid):
    if (not (g.user.is_root() or g.user.is_admin())) and g.user.uid != uid:
        return render_template('admin/403.html', message='You can only edit your self')
    if request.method == 'GET':
        user = user_service.get(uid)
        return render_template('admin/user/edit.html', statuses=User.STATUSES, roles=User.ROLES, user=user)

    p = request.form.get
    email = p('email')
    real_name = p('real_name')
    password = p('password', default='')
    newpass1 = p('newpass1')
    newpass2 = p('newpass2')
    bio = p('bio')
    status = p('status', default='inactive')
    role = p('role', default='user')

    result = user_service.update_user(
        uid, email, real_name, password, newpass1, newpass2, bio, status, role)
    if result['status'] == 'ok':
        return redirect(url_for('admin.user_edit', uid=result['user'].uid))
    else:
        flash(result['errors'], 'error')
        return redirect(url_for('admin.user_edit', uid=uid))
