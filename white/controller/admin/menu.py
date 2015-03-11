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
from flask import jsonify, request

from white.controller import admin_bp as bp, ADMIN, EDITOR
from white.security import security

from white.domain.menu import MenuService

menuservice = MenuService()


@bp.route('/menu')
@security(ADMIN)
def menu_page():
    pages = menuservice.menu(True)

    return render_template('admin/menu/index.html', messages='',
                           pages=pages)


@bp.route('/menu/update', methods=['GET', 'POST'])
@security(ADMIN)
def menu_update():
    sort = request.form.getlist('sort')

    menuservice.update(sort)

    return jsonify({'return': True})
