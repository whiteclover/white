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


from hashlib import sha256


def hide_pass_for_config(config):
    for key, value in config.iteritems():
        if ('pass' in key.lower() or 'secret' in key.lower()) and isinstance(value, (str, unicode)):
            config[key] = 'hide: %s' % (sha256(value).hexdigest())
        elif isinstance(value, dict):
            hide_pass_for_config(value)
