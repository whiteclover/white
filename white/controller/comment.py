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
from white.lang import text
from white.flash import flash


from white.controller import admin as bp, ADMIN, EDITOR
from white.security import security

from white.domain.comment import CommentService
from white.lang import text
from white.flash import flash
from white.lib.validator import Validator
from white.helper import site


comment_service = CommentService()

COMMENT_STATUSES = [
    {'url': 'all', 'lang': text('global.all'), 'class': 'all'},
    {'url': 'pending', 'lang': text('global.pending'), 'class': 'pending'},
    {'url': 'approved', 'lang': text('global.approved'), 'class': 'approved'},
    {'url': 'spam', 'lang': text('global.spam'), 'class': 'spam'}
]

@bp.route('/comment')
@bp.route('/comment/<status>')
@bp.route('/comment/<status>/<int:page>')
@security(EDITOR)
def comment_page(page=1, status='all'):
    pagination = comment_service.page(status, page, site.posts_per_page())
    return render_template('admin//comment/index.html',
            statuses=COMMENT_STATUSES,
            status=status,
            comments=pagination)


@bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@security(EDITOR)
def comment_edit(comment_id):
    if request.method == 'GET':
        statuses = {
            'approved' :text('global.approved'),
            'pending' :text('global.pending'),
            'spam' :text('global.spam')
        }
        comment = comment_service.get(comment_id)
        return render_template('admin/comment/edit.html', 
            comment=comment,
            statuses=statuses)

    p = request.form.get
    name = p('name')
    email = p('email')
    content = p('content')
    status = p('status')

    name, content = name.strip(), content.strip()

    validator = Validator()
    (validator.check(name, 'min', text('comment.name_missing'), 1)
        .check(content, 'min', text('comment.content_missing'), 1)
    )
    if validator.errors:
        flash(validator.errors, 'error')
        return redirect(url_for('admin.comment_edit', comment_id=comment_id))

    comment = comment_service.update_comment(comment_id, name, email, content, status)
    flash(text('comment.updated'), 'success')
    return redirect(url_for('admin.comment_edit', comment_id=comment.cid))


@bp.route('/comment/<int:comment_id>/delete')
@security(EDITOR)
def comment_delete(comment_id):
    comment_service.delete(comment_id)
    flash(text('comment.deleted'), 'success')
    return redirect(url_for('admin.comment_page'))


