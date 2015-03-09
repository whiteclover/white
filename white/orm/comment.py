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
from white.ext import db
from white.model import Comment


class CommentMapper(BaseMapper):

    table = 'comments'
    model = Comment

    def find(self, cid):
        data = db.select(self.table).fields('post_id', 'name',
         'email', 'content', 'status', 'created', 'cid').condition('cid', cid).execute()
        if data:
            return self.load(data[0], self.model)

    def find_by_post_id(self, post_id, status='approved'):
        q = db.select(self.table).fields('post_id', 'name',
         'email', 'content', 'status', 'created', 'cid').condition('post_id', post_id)
        if status:
            q.condition('status', status)
        data = q.execute()
        return [self.load(_, self.model) for _ in data]

    def paginate(self, page=1, perpage=10, status='all'):
        q = db.select(self.table).fields('post_id', 'name', 'email', 'content', 'status', 'created', 'cid')
        if status != 'all':
            q.condition('status', status)
        results = q.limit(perpage).offset((page - 1) * perpage).order_by('created').execute()
        pages = [self.load(page, self.model) for page in results]
        return pages

    def count(self):
        return db.select(self.table).fields(db.expr('COUNT(*)')).execute()[0][0]

    def spam_count(self, domain):
        return db.select(self.table).fields(db.expr('COUNT(*)')).condition('email', domain, 'LIKE').execute()[0][0]

    def create(self, comment):
        """Create a new comment"""
        return db.execute("INSERT INTO comments(post_id, name, email, content, status, created) VALUES(%s, %s, %s, %s, %s, %s)",
            (comment.post_id, comment.name, comment.email, comment.content, comment.status, comment.created))

    def save(self, comment):
        """Save Comment"""
        q = db.update(self.table)
        data = dict( (_, getattr(comment, _)) for _ in ('post_id', 'name',
         'email', 'content', 'status', 'created', 'cid'))
        q.mset(data)
        return q.condition('cid', comment.cid).execute()

    def delete(self, comment_id):
        """Delete category by commment id"""
        return db.delete(self.table).condition('cid', comment_id).execute()