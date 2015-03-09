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


__all__ = ['Backend']
__backends = {}


def Backend(name):
	return __backends.get(name)

def setup():
    from .user import UserMapper
    from .category import CategoryMapper
    from .page import PageMapper
    from .post import PostMapper
    from .extend import ExtendMapper
    from .meta import MetaMapper
    from .pair import PairMapper
    from .comment import CommentMapper
    __backends['user'] = UserMapper()
    __backends['category'] = CategoryMapper()
    __backends['page'] = PageMapper()
    __backends['post'] = PostMapper()
    __backends['extend'] = ExtendMapper()
    __backends['meta'] = MetaMapper()
    __backends['storage'] = PairMapper()
    __backends['comment'] = CommentMapper()
