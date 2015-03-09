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


from white.lib.memoize import memoize
from white.orm import Backend

@memoize()
def categories():
	return Backend('category').categories()

@memoize()
def menus():
	return Backend('page').menu(True)

@memoize()
def cached_user(uid):
	return Backend('user').find(uid)


class SiteConfig(object):

	def sitename(self):
		return self.config.get('sitename', 'White')

	def description(self):
		return self.config.get('site_description', '')

	def posts_per_page(self, perpage=10):
		return self.config.get('posts_per_page', perpage)


	def comment_moderation_keys(self):
		return self.config.get('comment_moderation_keys', [])

	def get(self, key, default=None):
		return self.config.get(key, default)

	@property
	def config(self):
		return self._config()

	@memoize()
	def _config(self):
		return Backend('storage').find('system').json_value()

	def clear_cache(self):
		self._config.cache.flush()


site = SiteConfig()