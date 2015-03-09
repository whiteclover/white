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


from datetime import datetime
from flask import g, request, flash, current_app, make_response, jsonify, abort
from flask import render_template, redirect, url_for, send_from_directory
from werkzeug.contrib.atom import AtomFeed

from white.domain.page import PageService
from white.domain.post import PostService
from white.domain.category import CategoryService
from white.domain.comment import CommentService
from white.orm import Backend
from white.helper import site as config

from white.controller.post import post_page
from white.lang import text
from white.flash import flash
from white.lib.validator import Validator
from white.lib.memoize import memoize
from white.ext import markdown
from urlparse import urljoin
from white.controller import site


post_service = PostService()
category_service = CategoryService()
comment_service = CommentService()
page_service = PageService()


def theme_render(tpl, *args, **kw):
    theme = current_app.config.get('THEME', 'default')
    tpl = 'theme/' + theme + '/' + tpl
    return render_template(tpl, *args, **kw)


@site.route('/content/<asset>')
def content_asset(asset):
    return send_from_directory(current_app.config['CONTENT_PATH'], asset)


def page_redirect():
    path = request.path
    page = page_service.get_by_redirect(path)
    if not page:
        return theme_render('404.html', page_title='Not Found'), 404
    return theme_render('page.html',
                        page_content=page.content,
                        page_title=page.title,
                        page=page)


@site.route('/')
@site.route('/<slug>')
def page(slug=None):
    if slug:
        if slug == 'admin':
            return post_page()
        elif slug == 'search':
            return search()
        elif slug == 'rss':
            return feed_rss()

        slug = slug.split('/')[-1]
        page = page_service.get_by_slug(slug)
    else:
        site_page = config.get('site_page', 0)
        if site_page == 0:
            return posts()
        else:
            page = page_service.get(site_page)

    if not page:
        abort(404)
    return theme_render('page.html',
                        page_content=page.content,
                        page_title=page.title,
                        page=page)


@site.route('/posts')
@site.route('/posts/<int:page>')
@site.route('/category/<category>')
@site.route('/category/<category>/<int:page>')
def posts(page=1, category=None):
    if page <= 0:
        theme_render('404.html')
    total, posts = post_service.get_published_posts_page(
        page, config.posts_per_page(), category)
    return theme_render('posts.html',
                        page_title='posts',
                        post_total=total,
                        posts=posts,
                        page_offset=page)


@site.route('/post/<slug>')
def post(slug):
    post = post_service.get_by_slug(slug)
    if not post:
        return theme_render('404.html')

    return theme_render('article.html',
                        page_title=post.title,
                        article=post,
                        comments=post.comments,
                        category=category_service.get_by_cid(post.category))


def search():
    key = request.args.get('q')
    page = request.args.get('page', type=int, default=1)
    pages = post_service.search(key, page)

    return theme_render('search.html',
                        page_title='Serach Article',
                        search_term=key,
                        articles=pages)


@site.route('/post/comment/<slug>', methods=['POST'])
def post_comment(slug):
    post = post_service.get_by_slug(slug)
    if not post:
        return theme_render('404.html', page_title='Not Found')

    if post and not post.allow_comment:
        return redirect(url_for('site.post', slug=slug))

    p = request.form.get
    name = p('name', default='')
    email = p('email', default='')
    content = p('content', default='')

    name, content, email = name.strip(), content.strip(), email.strip()

    validator = Validator()
    (validator.check(email, 'email', text('comment.email_missing'))
        .check(content, 'min', text('comment.email_missing'), 1)
     )

    if validator.errors:
        flash(validator.errors, 'error')
        return redirect(url_for('site.post', slug=slug))

    status = config.get(
        'auto_published_comments', False) and 'approved' or 'pending'
    comment_service.add_comment(name, email, content, status, post)

    return redirect(url_for('site.post', slug=slug))


@site.route('/feed/rss.json')
def feed_json():
    return jsonify(_feed_json())


@memoize(lifetime=30 * 60)
def _feed_json():
    posts = []
    for post in post_service.get_published_posts():
        data = dict(author=post.user.username,
                    html=markdown.convert(post.html),
                    url=urljoin(request.url_root,  '/post/' + post.slug),
                    updated=post.updated,
                    published=post.created
                    )
        posts.append(data)

    rss = {
        'sitename': config.sitename(),
        'site': request.url_root,
        'updated': datetime.now(),
        'description': config.description(),
        'posts': posts
    }
    return rss


@site.route('/feed/rss')
def feed_rss():
    response = make_response(_feed_rss())
    response.headers['Content-Type'] = 'application/xml'
    return response


@memoize(lifetime=30 * 60)
def _feed_rss():
    feed = AtomFeed(title=config.sitename(), subtitle='Recent Articles',
                    feed_url=request.url, url=request.url_root, updated=datetime.now())

    for post in post_service.get_published_posts():
        feed.add(post.title, markdown.convert(post.html),
                 content_type='html',
                 author=post.user.username,
                 url=urljoin(request.url_root,  '/post/' + post.slug),
                 updated=post.updated,
                 published=post.created)
    return ''.join(feed.generate())
