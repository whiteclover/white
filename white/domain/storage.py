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
from white.model import Pair
from flask.json import dumps
import re


class StorageService(object):

    def __init__(self):
        self.pair_repo = Backend('storage')

    def site_meta(self):
        return self.pair_repo.find('system')

    def update_site_meta(self, sitename, description, site_page,
                         posts_per_page, auto_published_comments,  comment_moderation_keys):

        meta = self.site_meta()
        config = meta.json_value()

        try:
            sitename = sitename or sitename.strip()
            if sitename:
                config['sitename'] = sitename

            description = description or description.strip()
            if description:
                config['description'] = description

            site_page = int(site_page)
            if site_page >= 0:
                config['site_page'] = site_page

            posts_per_page = int(posts_per_page)
            if posts_per_page:
                config['posts_per_page'] = posts_per_page

            auto_published_comments = bool(auto_published_comments)
            config['auto_published_comments'] = auto_published_comments
            if comment_moderation_keys is not None:
                keys = [key.strip() for key in re.split(' +', comment_moderation_keys) if key.strip()]
                config['comment_moderation_keys'] = keys
            meta.value = dumps(config)
            self.pair_repo.update(meta)
            return True
        except:
            return False
