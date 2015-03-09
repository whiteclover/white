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


from .base import BaseMapper
from white.ext  import db
from white.model import Page


class PageMapper(BaseMapper):

    table = 'pages'
    model = Page

    def find(self, pid):
        data = db.select(self.table).fields('parent', 'name', 'title', 'slug',
            'content', 'status', 'redirect', 'show_in_menu', 'pid').condition('pid', pid).execute()
        if data:
            return self.load(data[0], self.model)


    def find_by_redirect(self, redirect):
        data = db.select(self.table).fields('parent', 'name', 'title', 'slug',
            'content', 'status', 'redirect', 'show_in_menu', 'pid').condition('redirect', redirect).execute()
        if data:
            return self.load(data[0], self.model)

    def find_by_slug(self, slug):
        data = db.select(self.table).fields('parent', 'name', 'title', 'slug',
            'content', 'status', 'redirect', 'show_in_menu', 'pid').condition('slug', slug).execute()
        if data:
            return self.load(data[0], self.model)

    def menu(self, is_menu=False):
        q = db.select(self.table).fields('parent', 'name', 'title', 'slug',
            'content', 'status', 'redirect', 'show_in_menu', 'pid').condition('show_in_menu', 1)
        if not is_menu:
            res = q.execute()
        else:
            res = q.condition('status', 'published').order_by('menu_order').execute()
        return [self.load(data,self.model) for data in res]


    def dropdown(self, show_empty_option=True, exclude=[]):
        items = []
        if show_empty_option:
            items.append((0, '--'))

        pages = db.select(self.table).fields('pid', 'name').execute()
        for page in pages:
            if page[0] in exclude:
                continue
            items.append((page[0], page[1]))

        return items

    def count(self, status=None):
        q= db.select(self.table).fields(db.expr('COUNT(*)'))
        if status != 'all':
            q.condition('status', status)
        return q.execute()[0][0]


    def count_slug(self, slug):
        return db.select(self.table).fields(db.expr('COUNT(*)')).condition('slug', slug).execute()[0][0]

    def paginate(self, page=1, perpage=10, status='all'):
        q = db.select(self.table).fields('parent', 'name', 'title', 'slug',
            'content', 'status', 'redirect', 'show_in_menu', 'pid')
        if status != 'all':
            q.condition('status', status)
        results = q.limit(perpage).offset((page - 1) * perpage).order_by('title', 'desc').execute()
        pages = [self.load(page, self.model) for page in results]
        return pages

    def create(self, page):
        row = []
        for _ in ('parent', 'name', 'title', 'slug', 'content', 'status', 'redirect', 'show_in_menu'):
            row.append(getattr(page, _))
        return db.insert(self.table).fields('parent', 'name', 'title', 'slug',
            'content', 'status', 'redirect', 'show_in_menu').values(row).execute()
          
    def save(self, page):
        q = db.update(self.table)
        data = dict( (_, getattr(page, _)) for _ in ('parent', 'name', 
                'title', 'slug', 'content', 'status', 'redirect', 'show_in_menu'))
        q.mset(data)
        return q.condition('pid', page.pid).execute()

    def update_menu_order(self, pid, menu_order):
        return db.update(self.table).condition('pid', pid).set('menu_order', menu_order).execute()
        
    def delete(self, page_id):
        return db.delete(self.table).condition('pid', page_id).execute()
        