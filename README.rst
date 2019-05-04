bookstore
=========

The basic bookstore app built for SJSU Spring 2019 CMPE 272 course.

Builds
------

+---------------------+------------------------------------------------------------------------------------------+
| ``master``          | .. image:: https://travis-ci.com/karthikramasamy/cmpe-272.svg?branch=master              |
|                     |     :target: https://travis-ci.com/karthikramasamy/cmpe-272                              |
+---------------------+------------------------------------------------------------------------------------------+
| ``dev``             | .. image:: https://travis-ci.com/karthikramasamy/cmpe-272.svg?branch=dev                 |
|                     |     :target: https://travis-ci.com/karthikramasamy/cmpe-272                              |
+---------------------+------------------------------------------------------------------------------------------+

Code Coverage
-------------

+---------------------+------------------------------------------------------------------------------------------+
| ``master``          | .. image:: https://codecov.io/gh/karthikramasamy/cmpe-272/branch/master/graph/badge.svg  |
|                     |     :target: https://codecov.io/gh/karthikramasamy/cmpe-272                              |
+---------------------+------------------------------------------------------------------------------------------+
| ``dev``             | .. image:: https://codecov.io/gh/karthikramasamy/cmpe-272/branch/dev/graph/badge.svg     |
|                     |     :target: https://codecov.io/gh/karthikramasamy/cmpe-272                              |
+---------------------+------------------------------------------------------------------------------------------+

Install
-------

Download the source code::

    # clone the repository
    $ git clone https://github.com/karthikramasamy/cmpe-272
    $ cd cmpe-272

Install bookstore::

    $ pip install -e .

Run
---

::

    $ export FLASK_APP=bookstore
    $ export FLASK_ENV=development
    $ flask init-db
    $ flask run

Open http://127.0.0.1:5000 in a browser.


Test
----

::

    $ pip install '.[test]'
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
