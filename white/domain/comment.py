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


import re 

from white.orm import Backend
from white.model import Comment
from white.lib.paginator import Paginator
from white.lang import text
from white.helper import site


class CommentService(object):

    comment_repo = Backend('comment')

    get = lambda self, cid: self.comment_repo.find(cid)

    def get_by_post_id(self, post_id):
        return self.comment_repo.find_by_post_id(post_id)

    def page(self, status, page=1, perpage=10):
        total = self.comment_repo.count()
        pages = self.comment_repo.paginate(page, perpage, status)
        pagination = Paginator(pages, total, page, perpage, '/admin/comment')
        return pagination

    def add_comment(self, name, email, content, status, post):
        comment = Comment(post.pid, name, email, content, status)
        if self.is_spam(comment):
            comment.status = 'spam'
        cid= self.comment_repo.create(comment)
        comment.cid = cid
        return comment

    @classmethod
    def is_spam(self, comment):
        for word in site.comment_moderation_keys():
            if word.strip() and re.match(word, comment.content, re.I):
                return True

    	domain = comment.email.split('@')[1]
    	if self.comment_repo.spam_count(domain):
    		return True
    	return False

    def update_comment(self, comment_id, name, email, content, status):
        comment = self.get(comment_id)
        if not comment:
            return None
        comment.status = status
        comment.name = name 
        comment.content = content
        comment.email = email
        self.comment_repo.save(comment)
        return comment

    def delete(self, comment_id):
        comment = self.comment_repo.find(comment_id)
        if not comment:
            return None
        return self.comment_repo.delete(comment.cid)
