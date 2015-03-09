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
from white.model import Page
from white.lib.paginator import Paginator


class PageService(object):

    def __init__(self):
        self.page_repo = Backend('page')

    get = lambda self, pid: self.page_repo.find(pid)

    def get_by_redirect(self, redirect):
        return self.page_repo.find_by_redirect(redirect)

    def get_by_slug(self, slug):
        return self.page_repo.find_by_slug(slug)

    def dropdown(self, show_in_menu=True):
        return self.page_repo.dropdown(show_in_menu)

    def page(self, status, page=1, perpage=10):
        total = self.page_repo.count(status)
        pages = self.page_repo.paginate(page, perpage, status)
        if status:
            url = '/admin/page/status/' + status
        else:
            url = '/admin/page'
        pagination = Paginator(pages, total, page, perpage, url)
        return pagination

    def delete(self, page_id):
        page = self.page_repo.find(page_id)
        if not page:
            return None
        return self.page_repo.delete(page.pid)

    def add_page(self, parent, name, title, slug, content, status, redirect, show_in_menu):
        redirect = redirect.strip()
        show_in_menu = 1 if show_in_menu else 0
        page = Page(parent, name, title, slug, content, status, redirect, show_in_menu)
        pid = self.page_repo.create(page)
        page.pid = pid
        return page

    def is_exist_slug(self, slug):
        return self.page_repo.count_slug(slug) == 1

    def update_page(self, parent, name, title, slug, content, status, redirect, show_in_menu, pid):
        show_in_menu = 1 if show_in_menu else 0
        redirect = redirect.strip()
        page = Page(parent, name, title, slug, content, status, redirect, show_in_menu, pid)
        self.page_repo.save(page)
        return page
