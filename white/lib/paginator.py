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



from flask import Markup 

class Paginator(object):

    def __init__(self, results, total, page, perpage, url, glue='/'):
        self.results = results
        self.total = total
        self.page = page
        self.first = 'First'
        self.last = 'Last'
        self._next = 'Next'
        self._prev = 'Previous'
        self.perpage = perpage
        self.url = url
        self._index = 0
        self.glue = glue

    def next_link(self,  text='&larr; Previous', default=''):
        text = text or self._next
        pages = (self.total / self.perpage) + 1
        if self.page < pages:
            page = self.page + 1
            return '<a href="' + self.url + self.glue + str(page) + '">' + text + '</a>'

        return default

    def pre_link(self, text='&larr; Previous', default=''):
        text = text or self._prev
        if self.page > 1:
            page = self.page - 1
            return Markup('<a href="' + self.url + self.glue + str(page) + '">' + text + '</a>')

        return Markup(default)

    def links(self):
        html = ''
        pages = (self.total / self.perpage)
        if self.total % self.perpage != 0:
            pages += 1
        ranged = 4
        if pages > 1:
            if self.page > 1:
                page = self.page - 1
                html += '<a href="' + self.url + '">' + self.first + '</a>' + \
                    '<a href="' + self.url + self.glue + str(page) + '">' + self._prev + '</a>'
            for i in range(self.page - ranged, self.page + ranged):
                if i < 0:
                    continue
                page = i + 1
                if page > pages:
                    break

                if page == self.page:
                    html += '<strong style="color:black">' + str(page) + '</strong>'
                else:
                    html += '<a href="' + self.url + self.glue + str(page) + '">' + str(page) + '</a>'

            if self.page < pages:
                page = self.page + 1

                html += '<a href="' + self.url + self.glue + str(page) + '">' + self._next + '</a> <a href="' + \
                    self.url + self.glue + str(pages) + '">' + self.last + '</a>'

        return html

    __html__ = links

    def __len__(self):
        return len(self.results)

    def __iter__(self):
        return self

    def next(self):
        try:
            result = self.results[self._index]
        except IndexError:
            raise StopIteration
        self._index += 1
        return result

    __next__ = next  # py3 compat