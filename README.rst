XetCache
========

XetCache provides persistent caching of long running functions or
jupyter notebook cells.

The cache can be stored on local disk together with your notebooks and
code (and using LFS, or the git-xet extension to store it with your git
repo). Or alternatively, it can be fully managed by the
`XetHub <xethub.com>`__ service to easily share the cache with your
collaborators.

Table of Contents
=================

-  `Install <#install>`__
-  `Setup <#setup>`__

   -  `Setup With Local <#setup-with-local>`__
   -  `Setup with Git Storage <#setup-with-git-storage>`__
   -  `Setup With XetHub <#setup-with-xethub>`__

      -  `Authentication <#authentication>`__

         -  `Command Line <#command-line>`__
         -  `Environment Variable <#environment-variable>`__
         -  `In Python <#in-python>`__

-  `Usage <#usage>`__

   -  `Usage For Jupyter Notebooks <#usage-for-jupyter-notebooks>`__
   -  `Usage For Function Caching <#usage-for-function-caching>`__
   -  `Usage For Function Call
      Caching <#usage-for-function-call-caching>`__

-  `License <#license>`__

Install
=======

::

   pip install xetcache

Or to install from source from GitHub:

::

   pip install git+https://github.com/xetdata/xetcache.git

Setup
=====

Setup With Local
----------------

No additional set up needed. See Usage below.

Setup with Git Storage
----------------------

If using LFS, you can just directly commit and push the cache files in
the ``xmemo`` folder.

However, if using GitHub we recommend the use of `XetHub’s extensions to
GitHub <https://xetdata.com>`__ for performance and the ability to
lazily fetch cached objects.

For instance, a repository with the XetHub extension will allow you to
lazy clone the repository with

::

   git xet clone --lazy [repo]

which will avoid fetching any large cached objects until they are
actually needed.

Setup With XetHub
-----------------

The use of the fully managed XetHub service provides more powerful data
deduplication capabilities that allows similar objects to be stored or
loaded, without needing to upload or download everything. We can also
deploy caches near your compute workloads to accelerate dataloading by
over 10x.

Authentication
~~~~~~~~~~~~~~

Signup on `XetHub <https://xethub.com/user/sign_up>`__ and obtain a
username and access token. You should write this down.

There are three ways to authenticate with XetHub:

Command Line
^^^^^^^^^^^^

.. code:: bash

   xet login -e <email> -u <username> -p <personal_access_token>

Xet login will write authentication information to ``~/.xetconfig``

Environment Variable
^^^^^^^^^^^^^^^^^^^^

Environment variables may be sometimes more convenient:

.. code:: bash

   export XET_USER_EMAIL = <email>
   export XET_USER_NAME = <username>
   export XET_USER_TOKEN = <personal_access_token>

In Python
^^^^^^^^^

Finally if in a notebook environment, or a non-persistent environment,
we also provide a method to authenticate directly from Python. Note that
this must be the first thing you run before any other operation:

.. code:: python

   import pyxet
   pyxet.login(<username>, <personal_access_token>, <email>)

Usage
=====

*Optional* : to cache on XetHub, you need to run:

::

   import xetcache
   xetcache.set_xet_project([give a project name here])

Usage For Jupyter Notebooks
---------------------------

For Jupyter notebooks, run the following command to load the extension

.. code:: python

   import xetcache

After which adding the following line to the top of a cell

.. code:: python

   %%xetmemo input=v1,v2 output=v3,v4

will cache the specified output variables (v3,v4 here) each time it is
called. If called later with the same input values for v1,v2, the cached
value is returned and not reevaluated. The cache is persistent across
Python runs.

By default, the output will only be cached if the cell takes longer the
3 seconds to run. “always=True” can be added to the xetmemo arguments to
ignore the runime and to always cache:

::

   %%xetmemo input=v1,v2 output=v3,v4 always=True

Note that inputs can be anything picklable including functions.

A key parameter can be added to group the stored objects together.
Objects stored with one key will not be retrievable with a different key

.. code:: python

   %%xetmemo input=v1,v2 output=v3,v4 always=True key=experiment1

Usage For Function Caching
--------------------------

To cache the output of a function:

.. code:: python

   from xetcache import xetmemo

   @xetmemo
   def slowfunction(arg1, arg2):
      ...

   # Stores with a key
   @xetmemo(key="hello")
   def slowfunction(arg1, arg2):
      ...

By default, the output will only be cached if the cell takes longer the
3 seconds to run. “always=True” can be added to the xetmemo arguments to
ignore the runtime and to always cache:

.. code:: python

   # This will always cache irrespective of runtime
   @xetmemo(always=True)
   def slowfunction(arg1, arg2):
      ...

Usage For Function Call Caching
-------------------------------

To cache a function call:

.. code:: python

   def slowfn(x):
       ..do stuff..

   # caches the call to slowfn with argument x
   xeteval(slowfn, x)

   # Stores with a key
   xeteval("key", slowfn, x)

By default, the output will only be cached if the cell takes longer the
3 seconds to run. ``xeteval_always`` can be used instead to ignore the
runtime and to always cache:

.. code:: python

   # Store even if function is quick to run
   xeteval_always(quickfn, x)

   # Store with a key and to always store even the function is quick to run
   xeteval_always("key", quickfn, x)

License
=======

`BSD 3 <LICENSE>`__
