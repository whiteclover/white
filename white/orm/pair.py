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
from white.model import Pair


class PairMapper(BaseMapper):

    model = Pair
    table = 'storage'

    def lists(self, exclude=None, sorted=False):
        q = db.select(self.table)
        if sorted:
            q.sort_by('key')
        if exclude:
            db.condition('key', exculde, '<>')
        res = q.execute()
        return [self.load(row, self.model) for row in res]

    def find(self, key):
        data = db.select(self.table).condition('key', key).execute()
        if data:
            return self.load(data[0], self.model)

    def save(self, pair):
        return db.insert(self.table).values((pair.key, pair.value, pair.type)).execute()

    def update(self, pair):
        return db.update(self.table).set('value', pair.value).condition('key', pair.key).execute()

    def delete(self, pair):
        return db.delete(self.table).condition('key', pair.key).condition('type', pair.type).execute()
