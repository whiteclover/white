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
from flask import jsonify
from flask import session

from white.controller import admin_bp as bp, ADMIN, EDITOR
from white.security import security
from white.orm import Backend
from white.model import Category

from white.domain.category import CategoryService
from white.lang import text
from white.flash import flash
from white.lib.validator import Validator

category_service = CategoryService()


@bp.route('/category')
@bp.route('/category/<int:page>')
@security(ADMIN)
def category_page(page=1):
    pagination = category_service.page(page)
    return render_template('admin/category/index.html',
                           categories=pagination)


@bp.route('/category/add', methods=['GET', 'POST'])
@security(ADMIN)
def category_add():
    if request.method == 'GET':
        return render_template('admin/category/add.html')

    reqp = request.form
    title = reqp.get('title')
    slug = reqp.get('slug')
    description = reqp.get('description')

    validator = Validator()
    validator.check(title, 'min', text('category.title_missing'), 1)
    if validator.errors:
        flash(validator.errors, 'error')
        return render_template('admin/category/add.html')

    category_service.add_category(title, slug, description)
    return redirect(url_for('admin.category_page'))


@bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@security(ADMIN)
def category_edit(category_id):
    if request.method == 'GET':
        category = category_service.get_by_cid(category_id)
        return render_template('admin/category/edit.html', category=category)

    p = request.form.get
    title = p('title')
    slug = p('slug')
    description = p('description')

    validator = Validator()
    validator.check(title, 'min', text('category.title_missing'), 1)
    if validator.errors:
        flash(validator.errors, 'error')
        return redirect(url_for('admin.category_edit', category_id=category_id))

    category = category_service.update_category(
        category_id, title, slug, description)
    flash(text('category.updated'), 'success')
    return redirect(url_for('admin.category_edit', category_id=category.cid))


@bp.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
@security(ADMIN)
def category_delete(category_id):
    if category_id == 1:
        flash('The Uncategory cann\'t delete', 'error')
        return redirect(url_for('admin.category_page'))

    category_service.delete(category_id)
    flash(text('category.deleted'), 'success')
    return redirect(url_for('admin.category_page'))
