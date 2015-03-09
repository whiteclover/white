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


import os
from flask import Flask, request, redirect, url_for, current_app
from werkzeug import secure_filename

from white.lib.image import img_resize
from white.orm import Backend
from white.model import Extend, Meta, Field
from white.lib.paginator import Paginator
from white.lang import text


class ExtendService(object):

    def __init__(self):
        self.extend_repo = Backend('extend')
        self.meta_repo = Backend('meta')

    def get_by_eid(self, extend_id):
        return self.extend_repo.find(extend_id)

    def field_page(self, page=1, perpage=10):
        total = self.extend_repo.count()
        pages = self.extend_repo.paginate(page, perpage)
        pagination = Paginator(pages, total, page, perpage, '/admin/extend/field')
        return pagination


    def get_fields_by_type(self, type='post', node_id=None):
        extends = self.extend_repo.find_by_type(type)
        if node_id is None:
            load_meta = lambda extend: Meta(0, type, extend)
        else:
            load_meta = lambda extend: self.meta_repo.find(type, node_id, extend.eid) or Meta(0, type, extend)

        return [Field(extend, load_meta(extend)) for extend in extends]

    def count(self, key, type):
    	return self.extend_repo.count(key=key, type=type)

    def create_extend(self, type, key, label, field, attributes):
        extend = Extend(type, key, label, field, attributes)
        self.extend_repo.create(extend)
        return extend

    def update_extend(self, type, key, label, field, attributes, extend_id):
        extend = self.get_by_eid(extend_id)
        if not extend:
            return None
        extend.attributes = attributes
        extend.label = label
        self.extend_repo.save(extend)
        return extend

    def delete_extend(self, extend_id):
        field = self.extend_repo.find(extend_id)
        if not field:
            return None
        return self.extend_repo.delete(field)

    def prcoess_field(self, node, type='post'):
        FieldMananger(node, type).process()



class FieldMananger(object):

    def __init__(self, node, type='post'):
        self.node = node
        self.type = type

    def process(self):
        type = self.type
        item_id = self.node.pid
        data  = None
        for extend in Backend('extend').find_by_type(type):
            process = getattr(self, 'process_' + extend.field, None)
            #if process:
            
            data = process(extend)

            if data:
                meta = Backend('meta').find(type, item_id, extend.eid)
                if meta:
                    meta.data = data
                    Backend('meta').save(meta)
                else:
                    meta = Meta(item_id, type, extend.eid, data)
                    Backend('meta').create(meta)

    def process_image(self, extend):
        file = request.files['extend_' + extend.key]
        filename = secure_filename(file.filename)
        if filename:
            app = current_app._get_current_object()
            path = os.path.join(app.config['CONTENT_PATH'], filename)
            name, ext = filename.rsplit('.', 1)
            filename = self.type + '-' + self.node.slug + '.' + ext
            path = os.path.join(app.config['CONTENT_PATH'], filename)
            file.save(path)
            img_resize(path, self.get_size(extend))
            return {'name': filename, 'filename': filename}

    def get_size(self, extend):
        return extend.attributes['size']['width'], extend.attributes['size']['height']

    def process_file(self, extend):
        file = request.files['extend_' + extend.key]
        if filename:
            filename = secure_filename(file.filename)
            app = current_app._get_current_object()
            name, ext = filename.rsplit('.', 1)
            path = os.path.join(app.config['CONTENT_PATH'], filename)
            file.save(path)
            return {'name': filename, 'filename': filename}

    def process_text(self, extend):
        text = request.form.get('extend_' + extend.key)
        return {'text': text}

    def process_html(self, extend):
        html = request.form.get('extend_' + extend.key)
        return {'html': html}