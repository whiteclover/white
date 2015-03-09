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
from white.model import Category
from white.lib.paginator import Paginator
from white.lang import text

class CategoryService(object):

    def __init__(self):
        self.category_repo = Backend('category')
        self.post_repo = Backend('post')

    def get_by_cid(self, category_id):
        return self.category_repo.find(category_id)

    def dropdown(self):
        return self.category_repo.dropdown()

    def page(self, page=1, perpage=10):
        total = self.category_repo.count()
        pages = self.category_repo.paginate(page, perpage)
        pagination = Paginator(pages, total, page, perpage, '/admin/category')
        return pagination

    def add_category(self, title, slug, description):
        category = Category(title, slug, description)
        cid = self.category_repo.create(category)
        category.cid = cid
        return category

    def update_category(self, category_id, title, slug, description):
        slug = slug or title
        category = Category(title, slug, description, category_id)
        self.category_repo.save(category)
        return category

    def delete(self, category_id):
        if category_id == 1:
            return
        category = self.category_repo.find(category_id)
        if category and self.category_repo.delete(category_id):
            self.post_repo.reset_post_category(category_id)
