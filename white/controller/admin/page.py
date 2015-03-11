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


from flask import g, request, current_app
from flask import render_template, redirect, url_for

from white.orm import Backend
from white.model import Page
from white.lib.validator import Validator
from white.helper import site

from white.controller import admin_bp as bp, ADMIN, EDITOR
from white.security import security


from white.domain.page import PageService
from white.domain.extend import ExtendService
from white.lang import text
from white.flash import flash

PAGE_STATUSES = {
    'published': text('global.published'),
    'draft': text('global.draft'),
    'archived': text('global.archived'),
}

page_service = PageService()
extend_service = ExtendService()


@bp.route('/page')
@bp.route('/page/<int:page>')
@bp.route('/page/status/<status>')
@bp.route('/page/status/<status>/<int:page>')
@security(EDITOR)
def page_page(page=1, status='all'):
    pagination = page_service.page(status, page, site.posts_per_page())
    return render_template('admin/page/index.html',
                           status=status,
                           pages=pagination)


@bp.route('/page/<int:page_id>/edit', methods=['GET', 'POST'])
@security(EDITOR)
def page_edit(page_id):
    if request.method == 'GET':
        pages = Backend('page').dropdown(show_empty_option=True)
        page = Backend('page').find(page_id)
        fields = extend_service.get_fields_by_type('page', page_id)
        return render_template('admin/page/edit.html',
                               statuses=PAGE_STATUSES,
                               pages=pages,
                               page=page,
                               fields=fields)

    f = request.form
    parent = f.get('parent')
    name = f.get('name')
    title = f.get('title')
    name = name or title

    slug = f.get('slug')
    content = f.get('content')
    status = f.get('status')
    show_in_menu = f.get('show_in_menu', type=int, default=0)
    show_in_menu = 1 if show_in_menu else 0

    redirect_ = f.get('redirect')

    validator = Validator()
    (validator
        .check(title, 'min', text('page.title_missing'), 3)
        #.check(redirect, 'url', text('page.redirect_missing'))
     )

    if validator.errors:
        flash(validator.errors, 'error')
        return redirect(url_for('admin.page_edit', page_id=page_id))

    page = page_service.update_page(
        parent, name, title, slug, content, status, redirect_, show_in_menu, page_id)
    extend_service.prcoess_field(page, 'page')
    return redirect(url_for('admin.page_edit', page_id=page_id))


@bp.route('/page/add', methods=['GET', 'POST'])
@security(EDITOR)
def page_add():
    if request.method == 'GET':
        pages = Backend('page').dropdown(show_empty_option=True)
        fields = extend_service.get_fields_by_type('page')
        return render_template('admin/page/add.html',
                               statuses=PAGE_STATUSES,
                               pages=pages,
                               fields=fields)

    f = request.form
    parent = f.get('parent')
    name = f.get('name')
    title = f.get('title')
    name = name or title

    slug = f.get('slug')
    content = f.get('content')
    status = f.get('status')
    pid = f.get('pid', type=int)
    show_in_menu = f.get('show_in_menu', type=int)
    show_in_menu = 1 if show_in_menu else 0

    redirect_ = f.get('redirect')

    validator = Validator()
    validator.add(
        'duplicate', lambda key: page_service.is_exist_slug(key) == False)
    (validator
        .check(title, 'min', text('page.title_missing'), 3)
        .check(slug, 'min', text('page.slug_missing'), 3)
        .check(slug, 'duplicate', text('page.slug_duplicate'))
        .check(slug, 'regex', text('page.slug_invalid'), r'^[0-9_A-Za-z-]+$')
        #.check(redirect, 'url', text('page.redirect_missing'))
     )

    if validator.errors:
        flash(validator.errors, 'error')
        pages = Backend('page').dropdown(show_empty_option=True)
        fields = extend_service.get_fields_by_type('page')
        return render_template('admin/page/add.html',
                               statuses=PAGE_STATUSES,
                               pages=pages,
                               fields=fields)

    page = page_service.add_page(
        parent, name, title, slug, content, status, redirect_, show_in_menu)
    extend_service.prcoess_field(page, 'page')
    return redirect(url_for('admin.page_page'))


@bp.route('/page/<int:page_id>/delete')
@security(EDITOR)
def page_delete(page_id):
    page_service.delete(page_id)
    return redirect(url_for('admin.page_page'))
