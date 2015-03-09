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


from flask import render_template, redirect, url_for, g

from flask import g, request, current_app
from flask import jsonify
from flask import session

from white.controller import admin as bp, ADMIN, EDITOR
from white.security import security

from white.orm import Backend
from white.model import Category

from white.domain.post import PostService
from white.domain.category import CategoryService
from white.domain.extend import ExtendService
from white.lang import text
from white.flash import flash
from white.lib.validator import Validator
from white.helper import site

post_service = PostService()
category_service = CategoryService()
extend_service = ExtendService()

STATUSES = {
    'published': text('global.published'),
    'draft': text('global.draft'),
    'archived': text('global.archived'),
}


@bp.route('/post')
@bp.route('/post/<int:page>')
@bp.route('/post/category/<int:category>')
@security(EDITOR)
def post_page(page=1, category=None):
    pagination = post_service.page(page, site.posts_per_page(), category)
    return render_template('admin//post/index.html', 
            categories=category_service.dropdown(),
            posts=pagination,
            category=category)


@bp.route('/post/add', methods=['GET', 'POST'])
@security(EDITOR)
def post_add():
    if request.method == 'GET':
        fields = extend_service.get_fields_by_type('post')
        return render_template('admin/post/add.html', 
            statuses=STATUSES, 
            categories=category_service.dropdown(),
            fields=fields)

    p = request.form.get
    title = p('title', default='')
    description = p('description')
    category = p('category', type=int, default=1)
    status = p('status', default='draft')
    comments = p('comments', type=int, default=0)
    html = p('html')
    css = p('custom_css', default='')
    js = p('custom_js', default='')
    slug = p('slug')

    title = title.strip()
    slug = slug.strip() or title

    validator = Validator()
    (validator.check(title, 'min', text('post.title_missing'), 1)
        .check(slug, 'min', text('post.title_missing'), 1)
    )
    if validator.errors:
        flash(validator.errors, 'error')
        return render_template('admin/post/add.html')

    author = g.user
    post = post_service.add_post(title, slug, description, html, css, js, category, status, comments, author)
    extend_service.prcoess_field(post, 'post')
    return redirect(url_for('admin.post_page'))


@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@security(EDITOR)
def post_edit(post_id):
    if request.method == 'GET':
        fields = extend_service.get_fields_by_type('post', post_id)
        return render_template('admin/post/edit.html', 
            statuses=STATUSES, 
         categories=category_service.dropdown(),
         article= post_service.get_by_pid(post_id),
         fields=fields)

    p = request.form.get
    title = p('title', default='')
    description = p('description')
    category = p('category', type=int, default=1)
    status = p('status', default='draft')
    comments = p('comments', type=int, default=0)
    html = p('html')
    css = p('custom_css', default='')
    js = p('custom_js', default='')
    slug = p('slug')

    title = title.strip()
    slug = slug.strip() or title


    validator = Validator()
    (validator.check(title, 'min', text('post.title_missing'), 1)
        .check(slug, 'min', text('post.title_missing'), 1)
    )
    if validator.errors:
        flash(validator.errors, 'error')
        return redirect(url_for('admin.post_edit', post_id=post_id))

    post = post_service.update_post(title, slug, description, html, css, js, category, status, comments, post_id)
    extend_service.prcoess_field(post, 'post')
    flash(text('post.updated'), 'success')
    return redirect(url_for('admin.post_edit', post_id=post_id))


@bp.route('/poist/<int:post_id>/delete')
@security(EDITOR)
def post_delete(post_id):
    post_service.delete(post_id)
    flash(text('posts.deleted'), 'success')
    return redirect(url_for('admin.post_page'))
