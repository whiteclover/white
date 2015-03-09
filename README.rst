White
#########


White is a blog cms. it's based `Anchor-cms <https://github.com/anchorcms/anchor-cms>`_ that a blog cms wrote by php.
The White project keeps the most of achor-cms features, but pythonic and some new feartures:

#. markdown blog
#. custom field extension
#. rss feed
#. some monitor api for mananger
#. database connection pool
#. take advantage of Flask and Jinjia2


.. image:: https://github.com/thomashuang/white/blob/master/snap/home.png


Install
==============


Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    pip install -r requirements.txt

or::

Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    cd db # the path to the project
    python setup.py install

Development
===========

Fork or download it, then run:

.. code-block:: bash 

    cd db # the path to the project
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


Write python setting in a file, the setting class name must be 'Setting'

.. code-block:: python

	from white.setting import Config


	class Setting(Config):

	    DEBUG = True
	    
	    ## Flask Session module
	    # session
	    SECRET_KEY = '7oGwHH8NQDKn9hL12Gak9G/MEjZZYk4PsAxqKU4cJoY='
	    SESSION_TYPE = 'filesystem'
	    SESSION_FILE_DIR = '/var/www/$yoursite.com/cookies'


	    ###### 
	    # Wanna use redis session, please comment filesystem session settings
	    SESSION_TYPE = 'redis'
	    # import redis 
	    # SESSION_REDIS = redis.Redis()
	    # PERMANENT_SESSION_LIFETIME = datetime.timedelta(60)



	    SESSION_FILE_THRESHOLD = 100
	    SESSION_FILE_MODE = 0600


	    ## DB Config
	    DB_CONFIG  = {
	    	'db': 'white',
	        'user': 'white',
	        'passwd': 'white',
	        'host': 'localhost',

	        'max_idle' : 10 # the mysql timeout setting
	    }
	    DB_MAXCONN = 10
	    DB_MINCONN = 5

	    # the custom fields asset path
	    CONTENT_PATH = '/var/www/$yoursite.com/content'

	    LANGUAGE = 'zh_CN' # in ('zh_CN', 'zh_TW', 'en_GB')

	    THEME = 'default' # the froent theme name


If your wanna set session adapter pleas see more information in ``flask-session`` doc.


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



try run
--------------


.. code-block:: bash

	> python whited -c=conf/config -d
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader



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