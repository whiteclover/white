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


from hashlib import sha224
from datetime import datetime
from white.orm import Backend
from flask.json import loads, dumps
from white.helper import cached_user
from werkzeug.utils import cached_property
from flask import Markup, current_app
from white.ext import markdown

""" Domain Model """

class User(object):

    STATUSES = {
        'active': 'active',
        'inactive': 'inactive',
    }

    USER = 'user'
    ROOT = 'root'
    ADMIN = 'administrator'
    EDITOR = 'editor'
    ROLES = {
        # 'root' : 'root',
        'administrator': 'administrator',
        'editor': 'editor',
        'user': 'user'
    }

    def __init__(self, username, email, real_name, password, bio, status, role='user', uid=None):
        """If the user load from database, if will intialize the uid and secure password.
        Otherwise will hash encrypt the real password

        arg role enum: the string in ('root', 'user', 'editor', 'administrator')
        arg status enum: the string in ('active', 'inactive')
        arg password fix legnth string: the use sha224 password hash
        """
        self.username = username
        self.email = email
        self.real_name = real_name
        self.bio = bio
        self.status = status
        self.role = role

        if uid is not None:
            self.uid = uid
            self._password = password
        else:
            self._password = self.secure_password(password)

    def inactive(self):
        return self.status == 'inactive'

    def is_guest(self):
        return self.uid == 0

    def is_root(self):
        return self.uid == 1

    def is_admin(self):
        return self.role == self.ADMIN 

    def is_editor(self):
        return self.role == self.EDITOR

    def password():
        doc = "The password property."
        def fget(self):
            return self._password
        def fset(self, value):
            self._password = self.secure_password(value)
        def fdel(self):
            del self._password
        return locals()
    password = property(**password())

    def check(self, password):
        """Check the password"""
        return self._password == self.secure_password(password)

    @classmethod
    def secure_password(self, password):
        """Encrypt password to sha224 hash"""
        return sha224(password).hexdigest()

    def __json__(self):
        data = self.__dict__.copy()
        del data['_password']
        return data


class Category(object):

    def __init__(self, title, slug, description, cid=None):
        """The Category is used by post and page model. when load from database it takes the cid"""
        self.title = title
        self.slug = slug
        self.description = description
        if cid is not None:
            self.cid = cid

    def __str__(self):
        return '<Category cid: %d, title: %s, slug: %s>' % (self.cid, self.title, self.slug)

    def is_uncategory(self):
        return self.cid == 1

    def category_url(self):
        return '/category/' + self.slug

    def category_count(self):
        return Backend('post').category_count(self.cid)


class Page(object):

    def __init__(self, parent, name, title, slug, content, status, redirect, show_in_menu, pid=None):

        self.parent = parent
        self.name = name
        self.title = title
        self.slug = slug
        self.content = content
        self.status = status
        self.redirect = redirect
        self.show_in_menu = show_in_menu
        if pid:
            self.pid = pid


    def custom_field(self, key):
        extend = Backend('extend').field('page', key)
        return extend.value(self.pid, type='page')

    def url(self):
        segments = [self.slug]
        parent = self.parent
        Store = Backend('page')
        while parent:
            page = Store.find(parent)
            if page:
                segments.insert(0, page.slug)
                parent = page.parent
            else:
                break

        return '/' + '/'.join(segments)



class Extend(object):

    def __init__(self, type, key, label, field, attributes, eid=None):
        """The Extend simple model"""
        self.key = key
        self.label = label
        self.type = type
        self.field = field
        self.attributes = attributes or {}

        if eid:
            self.eid = eid

    def value(self, node_id, type='post'):
        meta = Backend('meta').find(type, node_id, self.eid)
        meta = meta or Meta(node_id, type, self.eid)
        return Field(self, meta)

    def __str__(self):
        return "<Extend key:%s, label:%s>" %(self.key, self.label)


class Meta(object):

    def __init__(self, node_id, type, extend, data=None, mid=None):
        self.node_id = node_id
        self.type = type
        self.extend = extend
        self.data = data or {}
        if mid:
            self.mid = mid

    def get(self, key, default=None):
        return self.data.get(key, default)


class Field(object):

    def __init__(self, extend, meta):
        self.extend = extend
        self.meta = meta

    def value(self):
        field = self.field
        if field == 'text':
            value = self.meta.get('text', '')
        elif field == 'html':
            value = markdown.convert(self.meta.get('html', ''))
        elif field in ('image', 'file'):
            f = self.meta.get('filename', '')
            if f:
                value = '/content/' + f
            else:
                value = ''
        return Markup(value)
        

    @property
    def field(self):
        return self.extend.field

    @property
    def key(self):
        return self.extend.key

    @property
    def label(self):
        return self.extend.label

    def __html__(self):
        field = self.field
        if field == 'text':
            value = self.meta.get('text', '')
            return '<input id="extend_"' + self.key + '" name="extend_' + self.key + \
                 '" type="text" value="' + value + '">'

        if field == 'html':
            value = self.meta.get('html', '')
            return '<textarea id="extend_' + self.key + '" name="extend_' + self.key + \
                '" type="text">' + value + '</textarea>'

        if field in ('file', 'image'):
            value = self.meta.get('filename', '')
            html = '<span class="current-file">'

            if value:
                html += '<a href="' + '/assets/content/' + value + '" target="_blank">' + value + '</a>'

            html += '</span><span class="file"> <input id="extend_' + self.key + '" name="extend_' + \
                    self.key + '" type="file"> </span>'

            return html

        return ''

    html  = __html__



class Pair(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value 

    def json_value(self):
        return loads(self.value)



class Post(object):

    def __init__(self, title, slug, description, html, css, js, category, status, allow_comment, 
        author=None, updated=None, created=None, pid=None):
        self.title = title
        self.slug = slug
        self.description = description


        self.html = html
        self.css = css
        self.js = js
        self.category = category
        self.status = status
        self.allow_comment = allow_comment
        self.author = author
        self.pid = pid

        self.updated = updated or datetime.now()
        self.created = created or datetime.now()


    @property
    def user(self):
        return cached_user(self.author)

    @cached_property
    def comments(self):
        return Backend('comment').find_by_post_id(self.pid)


    def __json__(self):
        data = self.__dict__.copy()
        del data['js']
        del data['css']
        del data['slug']
        del data['commments']
        return data


    def custom_field(self, key):
        extend = Backend('extend').field('post', key)
        return extend.value(self.pid, type='post')


class Comment(object):

    def __init__(self, post_id, name, email, content, status, created=None, cid=None):
        self.post_id = post_id
        self.name = name
        self.email = email
        self.content = content
        
        self.status = status
        self.created = created or datetime.now()
        self.cid = cid

    def __json__(self):
        return self.__dict__.copy()