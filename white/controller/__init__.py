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


from flask import Blueprint

admin = Blueprint('admin', 'admin')
site = Blueprint('site', 'site')


ADMIN, EDITOR  =  'administrator', 'editor'


from . import (
	user, 
	page,
	category,
	comment,
	extend,
	field,
	front,
	menu,
	post,
	metadata
)