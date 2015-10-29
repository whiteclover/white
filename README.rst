White
#########


White is a blog cms. it's based `Anchor-cms <https://github.com/anchorcms/anchor-cms>`_ that a blog cms wrote by php.
The White project keeps the most of achor-cms features, but pythonic and some new feartures:

#. write blog use markdown
#. custom field extension
#. custom theme
#. multi-languages support
#. rss feed
#. some monitor api for mananger
#. database connection pool
#. memozie cache
#. take advantage of Flask and Jinjia2


.. image:: https://github.com/thomashuang/white/blob/master/snap/home.png


.. contents::
    :depth: 2

Install
==============


Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    pip install -r requirements.txt

or::

Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    cd white # the path to the project
    python setup.py install

Development
===========

Fork or download it, then run:

.. code-block:: bash 

    cd white # the path to the project
    python setup.py develop

Compatibility
=============

Built and tested under Python 2.7 

Setup Database
==============

* create database in mysql:
* then run the mysql schema.sql script in the project directoy schema:

.. code-block:: bash

    mysql -u yourusername -p yourpassword yourdatabase < schema.sql


if your database has not been created yet, log into your mysql first using:

.. code-block:: bash

    mysql -u yourusername -p yourpassword yourdatabase
    mysql>CREATE DATABASE a_new_database_name
    # = you can =
    mysql> USE a_new_database_name
    mysql> source schema.sql



when firstly run the project, please use the root account, then go to user management ui change your account info:

:username: white 
:password: white


Setup Config file
=====================


Currently, using hocon config. the primary goal of hocon is: keep the semantics (tree structure; set of types; encoding/escaping) from JSON, but make it more convenient as a human-editable config file format.

.. code-block:: python

	HOST = "localhost" # server host
	PORT = 5000 # server port

	DEBUG = on # off # open debug mode


	## Flask Session module
	# session
	SECRET_KEY = "7oGwHH8NQDKn9hL12Gak9G/MEjZZYk4PsAxqKU4cJoY="
	SESSION_TYPE = "filesystem"
	SESSION_FILE_DIR = "/var/www/$yoursite.com/cookies"



	## Flask Session module
	# session
	SECRET_KEY = "7oGwHH8NQDKn9hL12Gak9G/MEjZZYk4PsAxqKU4cJoY="

	SESSION_TYPE = "filesystem" # "redis" 
	## REDIS_HOST = 127.0.0.1
	#PERMANENT_SESSION_LIFETIME = 60

	SESSION_FILE_DIR = "cookie"
	SESSION_FILE_THRESHOLD = 100
	SESSION_FILE_MODE = 0600

	SESSION_FILE_THRESHOLD = 100
	SESSION_FILE_MODE = 0600


	## DB Config
	DB_CONFIG  {
	    db = white
	    user = white
	    passwd = white
	    host = localhost

	    max_idle = 10 # the mysql timeout setting
	}

	# DB POOL Size 
	DB_MAXCONN = 10
	DB_MINCONN = 5


	# STATIC_FOLDER="pathTo/assets" # static folder if your wanna set custom you media assets

	CONTENT_PATH = "/var/www/$yoursite.com/content"
	LANGUAGE = "en_GB"
	THEME = "default"


If your wanna set session adapter please see more information in `flask-session <http://pythonhosted.org/Flask-Session/>`_ doc.


Run in console
================



The terminal help options
--------------------------


.. code-block:: bash

	> python whited -h
	usage: whited [options]

	optional arguments:
	  -h, --help            show this help message and exit
	  -host HOST, --host HOST
	                        the host for run server
	  -p PORT, --port PORT  the port for run server
	  -d, --debug           open debug mode (default False)
	  -c FILE, --config FILE
	                        config path (default '/etc/white/config')



Try run
--------------

If you wanna use production mode and ``whited`` running the blog service, please install ``gevent`` firstly. 

.. code-block:: bash

	> python whited -c=conf/config -d
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader


Run White in Other WSGI Servers
----------------------------------

When you wanna use other wsgi servers, just booststrap app, then take the app in your server api:

.. code-block:: python

	from white.server import WhiteServer

	server = WhiteServer()
	app = server.bootstrap()

	wsgi_server_run(app) # your wsgi warpper



Monitor Api
================

All apis require admin permisssion, please take admin user session.

DB status check
---------------------------------

	GET /admin/meta/db_status.json


.. code-block:: json

	{
	  "message": "Fine", 
	  "status": "ok"
	}


Get Application config
--------------------------


	GET /admin/meta/config.json


.. code-block:: json

	{
	  "APPLICATION_ROOT": null, 
	  "CONTENT_PATH": "$content_path", 
	  "CSRF_SECRET": "hide: e8c78f7bfe8eccf18b1e731a27a7e2835739a9c8a354559ad5eced4c5f76d909", 
	  "DB_CONFIG": {
	    "db": "white", 
	    "host": "localhost", 
	    "max_idle": 10, 
	    "passwd": "hide: d38681074467c0bc147b17a9a12b9efa8cc10bcf545f5b0bccccf5a93c4a2b79", 
	    "user": "white"
	  }, 
	  "DB_MAXCONN": 10, 
	  "DB_MINCONN": 5, 
	  "DEBUG": true, 
	  "HOST": "localhost", 
	  "JSONIFY_PRETTYPRINT_REGULAR": true, 
	  "JSON_AS_ASCII": true, 
	  "JSON_SORT_KEYS": true, 
	  "LANGUAGE": "en_GB", 
	  "LOGGER_NAME": "white", 
	  "MAX_CONTENT_LENGTH": null, 
	  "PERMANENT_SESSION_LIFETIME": "31 days, 0:00:00", 
	  "PORT": 5000, 
	  "PREFERRED_URL_SCHEME": "http", 
	  "PRESERVE_CONTEXT_ON_EXCEPTION": null, 
	  "PROPAGATE_EXCEPTIONS": null, 
	  "SECRET_KEY": "hide: dc5c40edf6c37edf0a7c615127d435b5aa8d0fcaccef4fde20f190aff81148fd", 
	  "SEND_FILE_MAX_AGE_DEFAULT": 43200, 
	  ...
	}



Get site meta
-------------------

	GET /admin/meta/meta.json



.. code-block:: json

	{
	  "auto_published_comments": true, 
	  "comment_moderation_keys": [], 
	  "description": "White is a Blog system", 
	  "posts_per_page": 10, 
	  "site_page": 0, 
	  "sitename": "White"
	}


Get current user info
------------------------

	GET /admin/user.json

.. code-block:: json
	
	{
	  "bio": "", 
	  "email": "white@demo.com", 
	  "real_name": "White", 
	  "role": "root", 
	  "status": "active", 
	  "uid": 1, 
	  "username": "white"
	}

LICENSE
=======

    2015 Copyright (C) White

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.