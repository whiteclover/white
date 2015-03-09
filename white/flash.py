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


from flask import flash as _flash, get_flashed_messages


class Flash(object):

    def __call__(self, errors, category):
        if not isinstance(errors, list):
            errors = [errors]
        for msg in errors:
            _flash(msg, category)

    def render(self):
        messages = get_flashed_messages(with_categories=True)
        if messages:
            html = '<div class="notifications">\n'
            for category, message in messages:
                html += '<p class="%s">%s</p>\n' % (category, message)
            html += '</div>'
            return html
        return ''

    __html__ = render


flash = Flash()
