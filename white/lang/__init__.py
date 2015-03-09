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


import codecs
import os
import os.path

from lilac.config import config


def setup(language=None):
    global __lines
    language = language or 'en_GB'
    langpath = os.path.join(os.path.dirname(__file__), language)
    __lines = {}
    for root, dirs, files in os.walk(langpath):
        for file in files:
            name, ext = file.split('.')
            if ext == 'py' and name != '__init__':
                ns = {}
                with codecs.open(os.path.join(langpath, file), "r", "utf-8") as f:
                    code = f.read()
                    exec code in ns
                    __lines[name] = ns['t']


def text(key, default=None, args=None):
    parts = key.split('.')
    if len(parts) == 2:
        name = parts[0]
        key = parts[1]
    if len(parts) == 1:
        name = 'global'
        key = parts.pop(0)

    t = __lines.get(name)
    if t:
        text = t.get(key, default)
        if text and args:
            text = text % args
    else:
        text = default
    return text
