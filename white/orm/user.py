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


from white.model import User
from white.ext  import db
from .base import BaseMapper


class UserMapper(BaseMapper):

    model = User
    table = 'users'

    def find(self, uid):
        """Find and load the user from database by uid(user id)"""
        data = (db.select(self.table).select('username', 'email', 'real_name',
                'password', 'bio', 'status', 'role', 'uid').
                condition('uid', uid).execute()
                )
        if data:
            return self.load(data[0], self.model)

    def find_by_username(self, username):
        """Return user by username if find in database otherwise None"""
        data = (db.select(self.table).select('username', 'email', 'real_name',
                'password', 'bio', 'status', 'role', 'uid').
                condition('username', username).execute()
                )
        if data:
            return self.load(data[0], self.model)

    def find_by_email(self, email):
        """Return user by email if find in database otherwise None"""
        data = (db.select(self.table).select('username', 'email', 'real_name',
                'password', 'bio', 'status', 'role', 'uid').
                condition('email', email).execute()
                )
        if data:
            return self.load(data[0], self.model)


    def create(self, user):
        return db.execute("INSERT INTO users(username, email, real_name, password, bio, status, role) \
             VALUES(%s, %s, %s, %s, %s, %s, %s)",
                          (user.username, user.email, user.real_name, user.password, user.bio, user.status, user.role))

    def search(self, **kw):
        """Find the users match the condition in kw"""
        q = db.select(self.table).condition('status', 'active')
        for k, v in kw:
            q.condition(k, v)
        data = q.execute()
        users = []
        for user in data:
            users.append(self.load(user, self.model))
        return users

    def count(self):
        return db.query('SELECT COUNT(*) FROM ' + self.table)[0][0]

    def take(self, page=1, perpage=10):
        count = self.count()
        q = db.select(self.table).select('username', 'email', 'real_name',
                                         'password', 'bio', 'status', 'role', 'uid')
        results = q.limit(perpage).offset((page - 1) * perpage).order_by('real_name', 'desc').execute()
        users = [self.load(user, self.model) for user in results]
        return users

    def save(self, user):
        q = db.update(self.table)
        data = dict( (_, getattr(user, _)) for _ in ('username', 'email', 'real_name', 'password',
                 'bio', 'status', 'role'))
        q.mset(data)
        return q.condition('uid', user.uid).execute()

    def delete(self, user):
        return db.delete(self.table).condition('uid', user.uid).execute()
