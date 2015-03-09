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


from white.orm import Backend
from white.model import User
from white.lib.paginator import Paginator
from flask import session, g
from white.lang import text
from white.lib.validator import EmailValidator
import re 


email_validator = EmailValidator()


class UserService(object):

    def __init__(self):
        self.repo = Backend('user')

    get = lambda self, uid: self.repo.find(uid)

    def auth(self, username, password):
        user = self.repo.find_by_username(username)
        if not user:
            return {'status' : 404, 'msg': 'not found'}

        if user and not user.inactive() and user.check(password):
            return {'status' : 200, 'msg': 'auth success', 'user': user}
        return {'status' : 403, 'msg': 'username or password is invaild'}

    def login(self, user):
        session.permanent = True
        session['auth'] = user.uid

    def logout(self):
        session.pop('auth', None)

    def page(self, page, perpage=5):
        total = self.repo.count()
        users = self.repo.take(page, perpage)
        page = Paginator(users, total, page, perpage, '/admin/user')
        return page
    
    def user_count(self):
        return self.repo.count()

    def check_email(self, email):
        return email_validator(email)

    def add_user(self, username, email, real_name, password, bio, status='', role='user'):
        username, real_name = username.strip(), real_name.strip()
        errors = []
        if not re.match(r'^[A-Za-z0-9_]{4,16}$', username):
            errors.append(text('user.username_missing'))

        if not re.match(r'^[A-Za-z0-9_]{4,16}$', password):
            errors.append(text('user.password_invalid'))

        if not self.check_email(email):
            errors.append(text('user.email_missing'))

        if errors:
            return {'status': 'error', 'errors': errors}

        if status not in User.STATUSES:
            status = 'inactive'

        if role not in User.ROLES:
            role = 'user'

        if self.repo.find_by_username(username):
             errors.append(text('user.username_used'))
        
        if errors:
            return {'status': 'error', 'errors': errors}

        user = User(username, email, real_name, password, bio, status, role)
        user.uid = self.repo.create(user)
        return  {'status': 'ok', 'msg': 'saved', 'user': user}

    def update_user(self, uid, email, real_name, password, newpass1, newpass2, bio, status, role='user'):
        real_name, newpass1, newpass2, bio = real_name.strip(), newpass1.strip(), newpass2.strip(), bio.strip()
        errors = []

        if not self.check_email(email):
            errors.append(text('user.email_missing'))

        if errors:
            return {'status': 'error', 'errors': errors}

        user = self.repo.find(uid)
        if not user:
            return {'status': 'error', 'errors': 'User not Found'}

        me = g.user
        if me.uid == user.uid:
            if re.match(r'[A-Za-z0-9@#$%^&+=]{4,16}', newpass1):
                if password and newpass1 and newpass1 == newpass2 and user.check(password):
                    user.password = newpass1
            elif newpass1:
                errors.append(text('users.password_missing'))

            if self.check_email(email):
                user_ = self.repo.find_by_email(email)
                if user_ and user_.uid != user.uid:
                    errors.append(text('user.email_used'))
                else:
                    user.email = email

        if errors:
            return {'status': 'error', 'errors': errors}


        if me.is_root() or me.uid == uid:
            if me.is_root() and not user.is_root():
                if role in (User.ADMIN, User.USER. User.EDITOR):
                    user.role = role
                if user.status != status and status in User.STATUSES:
                    user.status = status

            if user.real_name != real_name:
                user.real_name = real_name

            if user.bio != bio:
                user.bio = bio

        self.repo.save(user)
        return  {'status': 'ok', 'msg': 'updated', 'user': user}