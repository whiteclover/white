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
from white.model import Post



class PostMapper(BaseMapper):

    table = 'posts'
    model = Post

    def get_published_posts(self, page=1, perpage=10, category=None):
        q = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author', 'updated', 'created', 'pid')
        if category:
            q.condition('category', category)
        results = (q.limit(perpage).offset((page - 1) * perpage).condition('status', 'published')
                    .order_by('created', 'DESC').execute())
        return [self.load(data, self.model) for data in results]

    def find_by_slug(self, slug):
        data = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author', 'updated', 'created', 'pid').condition('slug', slug).execute()
        if data:
            return self.load(data[0], self.model)

    def search(self, key, page=1, perpage=10):
        q = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author', 'updated', 'created', 'pid')
        _or = db.or_()
        _or.condition('slug', '%%%s%%' %key, 'LIKE').condition('title','%%%s%%' %key, 'LIKE')
        q.condition(_or)
        results = (q.condition('status', 'published').limit(perpage).offset((page - 1) * perpage)
                    .order_by('created', 'DESC').execute())
        return [self.load(data, self.model) for data in results]
    

    def serach_count(self, key):
        q = db.select(self.table).fields(db.expr('count(*)', 
            'total')).condition('status', 'published')
        _or = db.or_()
        _or.condition('slug', '%%%s%%' %key, 'LIKE').condition('title','%%%s%%' %key, 'LIKE')
        q.condition(_or)
        return q.execute()[0][0]

    def find(self, pid):
        data = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author', 'updated', 'created', 'pid').condition('pid', pid).execute()
        if data:
            return self.load(data[0], self.model)

    def count(self, status=None):
        q= db.select(self.table).fields(db.expr('COUNT(*)'))
        if status:
            q.condition('status', status)
        return q.execute()[0][0]

    def create(self, post):
        row = []
        for _ in ('title', 'slug', 'description', 'updated', 'created', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author'):
            row.append(getattr(post, _))
        return db.insert(self.table).fields('title', 'slug', 'description', 'updated', 'created', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author').values(row).execute()

    def paginate(self, page=1, perpage=10, category=None, status=None):
        """Paginate the posts"""
        q = db.select(self.table).fields('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'author', 'updated', 'created', 'pid')
        if category:
            q.condition('category', category)
        if status:
            q.condition('status', status)
        results = (q.limit(perpage).offset((page - 1) * perpage)
                    .order_by('created', 'DESC').execute())
        return [self.load(data, self.model) for data in results]

    def reset_post_category(self, category_id):
        return db.update(self.table).set('category', 1).condition('category', category_id).execute()

    def save(self, page):
        q = db.update(self.table)
        data = dict( (_, getattr(page, _)) for _ in ('title', 'slug', 'description', 'html', 'css', 'js', 
            'category', 'status', 'allow_comment', 'updated'))
        q.mset(data)
        return q.condition('pid', page.pid).execute()

    def delete(self, page_id):
        return db.delete(self.table).condition('pid', page_id).execute()

    def category_count(self, category_id):
        return db.select(self.table).fields(db.expr('count(*)', 
            'total')).condition('category', category_id).condition('status', 'published').execute()[0][0]
