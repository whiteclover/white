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


from flask import render_template

from white.controller import admin_bp as bp, ADMIN, EDITOR
from white.security import security


@bp.route('/extend')
@security(ADMIN)
def extend_index():
    return render_template('admin/extend/index.html')

@bp.route('/extend/variable')
@security(ADMIN)
def variable_index():
    return render_template('admin/extend/variable/index.html')

@bp.route('/extend/variable/add')
@security(ADMIN)
def variable_add_page():
    return render_template('admin/extend/variable/add.html')

@bp.route('/extend/plugin')
@security(ADMIN)
def extend_plugin():
    return render_template('admin/extend/plugin/index.html') 