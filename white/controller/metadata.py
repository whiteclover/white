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


import re
from sys import exc_info

from flask import render_template, jsonify, request, redirect, url_for, current_app
from flask.json import loads, dumps

from white.orm import Backend
from white.lang import text
from white.flash import flash
from white.domain.storage import StorageService
from white.domain.page import PageService
from white.lib.validator import Validator
from white.helper import site
from white.util import hide_pass_for_config
from white.ext import db

from white.controller import admin as bp, ADMIN, EDITOR
from white.security import security


page_service = PageService()
storage_service = StorageService()


META_KEYS = ('sitename', 'description', 'site_page',
             'posts_per_page', 'auto_published_comments',  'comment_moderation_keys')


@bp.route('/meta/db_status.json')
@security(ADMIN)
def db_status():
    try:
        db.query('SELECT 1')
        status = {'status': 'ok', 'message': 'Fine'}
    except:
        cls, e, tb = exc_info()
        message = 'DB Error: %s' % (e)
        status = {'status': 'error', 'message': message}
    return jsonify(status)


@bp.route('/meta/meta.json')
@security(ADMIN)
def meta_json():
    pair = storage_service.site_meta()
    data = pair.json_value()
    config = {key: data[key] for key in META_KEYS}
    return jsonify(config)


@bp.route('/meta/config.json')
@security(ADMIN)
def site_config():
    config = current_app.config.copy()
    config['PERMANENT_SESSION_LIFETIME'] = str(
        config['PERMANENT_SESSION_LIFETIME'])
    hide_pass_for_config(config)
    return jsonify(config)


@bp.route('/extend/metadata', methods=['GET', 'POST'])
@security(ADMIN)
def metadata_page():
    if request.method == 'GET':
        pair = storage_service.site_meta()
        data = pair.json_value()
        data['comment_moderation_keys'] = ','.join(
            data['comment_moderation_keys'])
        pages = page_service.dropdown(False)
        configs = {key: data[key] for key in META_KEYS}
        return render_template('admin/extend/metadata/edit.html',
                               pages=pages,
                               **configs)

    p = request.form.get
    sitename = p('sitename')
    description = p('description')
    site_page = p('site_page', type=int, default=0)
    posts_per_page = p('posts_per_page', type=int, default=0)
    auto_published_comments = p('auto_published_comments', type=bool)
    comment_moderation_keys = p('comment_moderation_keys')

    storage_service.update_site_meta(sitename, description, site_page,
                                     posts_per_page, auto_published_comments,  comment_moderation_keys)
    site.clear_cache()
    flash(text('metadata.updated'), 'success')
    return redirect(url_for('admin.metadata_page'))
