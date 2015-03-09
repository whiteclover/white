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
from white.lib.paginator import Paginator


class MenuService(object):

    def __init__(self):
        self.page_repo = Backend('page')

    def menu(self, page=1):
        pages = self.page_repo.menu(True)
        return pages

    def update(self, sort):
        for menu_order, pid in enumerate(sort):
            self.page_repo.update_menu_order(pid, menu_order)
