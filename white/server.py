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

import codecs


from flask import Flask
from white.patch import patch_flask


class WhiteServer(object):

    def __init__(self):
        patch_flask()
        self.app = Flask(
            'white', template_folder='view', static_folder='asset')
        self.options = self.cmd_options()

    def cmd_options(self):
        from argparse import ArgumentParser
        parser = ArgumentParser(usage="whited [options]")
        _ = parser.add_argument
        _('-host', '--host', help='the host for run server',
          default=None)
        _('-p', '--port', help='the port for run server',
          type=int, default=None)
        _("-d", "--debug", action='store_true', default=False,
          help="open debug mode (default %(default)r)")
        _("-c", "--config", default='/etc/white/config',
          help="config path (default %(default)r)", metavar="FILE")
        return parser.parse_args()

    def bootstrap(self):
        self.bootstrap_setting()
        self.bootstrap_database()
        self.bootstrap_hooks()
        self.bootstrap_routes()
        self.bootstrap_errorpage()

        return self.app

    def bootstrap_setting(self):
        config = self.load_config()
        if not config:
            raise Exception("Load App Setting failed")
        self.app.config.from_object(config)

        if self.options.debug:
            self.app.config['DEBUG'] = True
            self.app.debug = True

        if self.options.host is not None:
            self.app.config['HOST'] = self.options.host

        if self.options.port is not None:
            self.app.config['port'] = self.options.port

        from white.ext import session
        session.app = self.app
        session.init_app(self.app)

        from white import lang
        from white.lang import text
        from white.flash import flash
        from white.helper import categories, menus, site
        from white.ext import markdown
        lang.setup(self.app.config.get('LANGUAGE', 'en_GB'))

        self.app.jinja_env.globals.update(__=text)
        self.app.jinja_env.globals.update(
            flash=flash, site_categories=categories, menus=menus)
        self.app.jinja_env.globals.update(site=site, enumerate=enumerate)

        self.app.jinja_env.filters['markdown'] = markdown.convert

    def load_config(self):
        with codecs.open(self.options.config, "r", "utf-8") as f:
            code = f.read()
            ns = {}
            exec code in ns
            return ns.get('Setting')

    def bootstrap_errorpage(self):
        from flask import render_template
        from white.controller.front import page_redirect, theme_render

        @self.app.errorhandler(403)
        def forbidden(e):
            return theme_redner('403.html'), 403

        @self.app.errorhandler(404)
        def not_found(e):
            return page_redirect()

    def bootstrap_hooks(self):
        """Hooks for request."""
        from white.security import init_user

        self.app.before_request(init_user)

    def bootstrap_database(self):
        """Init Database Settings"""
        from white.ext import db
        from white import orm

        config = self.app.config.get('DB_CONFIG')
        minconn = self.app.config.get('MINCONN', 5)
        maxconn = self.app.config.get('MAXCONN', 10)
        db.setup(config, minconn=minconn, maxconn=maxconn)

        orm.setup()

    def bootstrap_routes(self):
        from white.controller import admin, site
        self.app.register_blueprint(admin, url_prefix='/admin')
        self.app.register_blueprint(site, url_prefix='')

    def serve_forever(self):
        from gevent.wsgi import WSGIServer
        debug = self.app.config.get('DEBUG', True)
        host = self.app.config.get('HOST', 'localhost')
        port = self.app.config.get('port', 5000)
        if not debug:
            http_server = WSGIServer((host, port), self.app, log=debug)
            http_server.serve_forever()
        else:
            self.app.run(host, port)
