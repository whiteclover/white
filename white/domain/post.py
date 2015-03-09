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
from white.model import Post
from white.lib.paginator import Paginator
from white.lang import text
from datetime import datetime

class PostService(object):

    def __init__(self, post_repo=None, category_repo=None):
        self.post_repo = post_repo or Backend('post')
        self.category_repo = category_repo or Backend('category')

    def get_by_pid(self, post_id):
        return self.post_repo.find(post_id)


    def get_published_posts(self, page=1, perpage=10, category=None):
        return self.post_repo.get_published_posts(page, perpage, category)

    def get_published_posts_page(self, page=1, perpage=10, category=None):
        cid = None
        if category:
            real_category = self.category_repo.find_by_slug(category)
            if not real_category:
                return Paginator([], 0, page, perpage, '/category/' + category)
            cid = real_category.cid
        
        total = self.post_repo.category_count(cid)
        pages = self.post_repo.get_published_posts(page, perpage, cid)
        url = 'category/' + category if category else '/posts'
        pagination = Paginator(pages, total, page, perpage, url)
        return total, pagination

    def search(self, key, page, perpage=10):
        pages = self.post_repo.search(key, page, perpage)
        total = self.post_repo.serach_count(key)
        pagination = Paginator(pages, total, page, perpage, '/admin/post')
        return pagination

    def get_by_slug(self, slug):
        return self.post_repo.find_by_slug(slug)

    def lists(self, page=1, perpage=10):
        total = self.post_repo.count()
        pages = self.post_repo.paginate(page, perpage)
        pagination = Paginator(pages, total, page, perpage, '/posts')
        
        return total, pagination

    def page(self, page=1, perpage=10, category=None):
        total = self.post_repo.count(category)
        pages = self.post_repo.paginate(page, perpage, category)
        pagination = Paginator(pages, total, page, perpage, '/admin/post')
        return pagination

    def post_count(self, category_id=None):
        if category_idi is not None:
            return self.post_repo.count()
        return self.post_repo.category_count(category_id)

    def add_post(self, title, slug, description, html, css, js, category, status, comments, author):
        css, js, description = css.strip(), js.strip(), description.strip()
        comments = 1 if comments else 0
        if not html.strip():
            status = 'draft'

        post = Post(title, slug, description, html, css, js, category, status, comments, author.uid)
        post.created = datetime.now()
        pid = self.post_repo.create(post)
        post.pid = pid
        return post

    def update_post(self, title, slug, description, html, css, js, category, status, comments, post_id):
        css, js, description = css.strip(), js.strip(), description.strip()
        post = self.get_by_pid(post_id)
        if not html.strip():
            status = 'draft'

        post.title = title
        # post.slug = slug
        post.description = description
        post.html = html
        post.css = css
        post.js = js 

        post.updated = datetime.now()

        post.category = category
        post.status = status
        post.allow_comment = 1 if comments else 0
        self.post_repo.save(post)

        return post

    def delete(self, post_id):
        post = self.post_repo.find(post_id)
        if not post:
            return None
        return self.post_repo.delete(post.pid)
