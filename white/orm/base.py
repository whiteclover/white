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


from white.ext  import db


class BaseMapper(object):

    def load(self, data, o):
        return o(*data)


class PrimaryTrait(object):

    primary_id = 'id'

    def find(self, id):
        q = db.select(self.table).condition(self.primary_id, id)
        data = q.query()
        if data:
            return self.load(data[0], self.model)