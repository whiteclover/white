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


from flask import render_template, redirect, url_for

from flask import g, request, current_app
from flask.json import dumps
from flask import session

from white.controller import admin_bp as bp, ADMIN, EDITOR
from white.security import security

from white.orm import Backend

from white.domain.extend import ExtendService
from white.lang import text
from white.flash import flash
from white.lib.validator import Validator

extend_service = ExtendService()


@bp.route('/extend/field')
@bp.route('/extend/field/<int:page>')
@security(ADMIN)
def field_page(page=1):
    extends = extend_service.field_page(page)
    return render_template('admin//extend/field/index.html', fields=extends)


@bp.route('/extend/field/add', methods=['GET', 'POST'])
@security(ADMIN)
def field_add():
    if request.method == 'GET':
        return render_template('admin//extend/field/add.html')

    reqp = request.form
    _type = reqp.get('type')
    field = reqp.get('field')
    key = reqp.get('key')
    label = reqp.get('label')
    key = key or label

    validator = Validator()
    validator.add(
        'valid_key', lambda key: extend_service.count(key, _type) == 0)
    (validator
        .check(key, 'min', text('extend.key_missing'), 1)
        .check(key, 'valid_key', text('extend.key_exists'))
        .check(label, 'min', text('extend.label_missing'), 1)
     )

    if validator.errors:
        flash(validator.errors, 'error')
        return render_template('admin/extend/field/add.html')

    if field == 'image':
        attributes = {
            'type': reqp.get('attributes[type]'),
            'size': {
                'height': reqp.get('attributes[size][height]', type=int),
                'width': reqp.get('attributes[size][width]', type=int),
            }
        }
    elif field == 'file':
        attributes = {
            'type': reqp.get('attributes[type]'),
        }
    else:
        attributes = {}

    extend_service.create_extend(_type, key, label, field, attributes)
    return redirect(url_for('admin.field_page'))


@bp.route('/extend/field/<int:extend_id>/edit', methods=['GET', 'POST'])
@security(ADMIN)
def field_edit(extend_id):
    if request.method == 'GET':
        extend = extend_service.get_by_eid(extend_id)
        return render_template('admin//extend/field/edit.html', field=extend)

    reqp = request.form
    _type = reqp.get('type')
    field = reqp.get('field')
    key = reqp.get('key')
    label = reqp.get('label')
    key = key or label

    validator = Validator()
    (validator
        .check(key, 'min', text('extend.key_missing'), 1)
        .check(label, 'min', text('extend.label_missing'), 1)
     )

    if validator.errors:
        flash(validator.errors, 'error')
        return redirect(url_for('admin.field_edit', extend_id=extend_id))

    if field == 'image':
        attributes = {
            'type': reqp.get('attributes[type]'),
            'size': {
                'height': reqp.get('attributes[size][height]', type=int),
                'width': reqp.get('attributes[size][width]', type=int),
            }
        }
    elif field == 'file':
        attributes = {
            'type': reqp.get('attributes[type]'),
        }
    else:
        attributes = {}

    extend_service.update_extend(
        _type, key, label, field, attributes, extend_id)
    return redirect(url_for('admin.field_edit', extend_id=extend_id))


@bp.route('/extend/field/<int:extend_id>/delete')
@security(ADMIN)
def field_delete(extend_id):
    extend_service.delete_extend(extend_id)
    return redirect(url_for('admin.field_page'))
