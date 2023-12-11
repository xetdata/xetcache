# XetCache

XetCache provides persistent caching of long running functions or jupyter
notebook cells. 

The cache can be stored on local disk together with your notebooks and code
(and using LFS, or the git-xet extension to store it with your git repo).
Or alternatively, it can be fully managed by the [Xethub](xethub.com) service
to easily share the cache with your collaborators.

# Install
```
pip install xetcache
```

Or to install from here:

```
pip install git+https://github.com/xetdata/xetcache.git
```

# Setup With Local / Git storage
No additional set up needed. See Usage below.

However, if using a git repository in Github
we recommend the use of [Xethub's extensions to Github](https://xetdata.com)
for performance and the ability to lazily fetch cached objects.

For instance, a repository with the Xethub extension will allow you to
lazy clone the repository with 
```
git xet clone --lazy [repo]
```
which will avoid fetching any large cached objects until they are 
actually needed.

# Setup With Xethub
The use of the fully managed XetHub service provides more powerful data
deduplication capabilities that allows similar objects to be stored or loaded,
without needing to upload or download everything. We can also deploy caches near
your compute workloads to accelerate dataloading by over 10x.

## Authentication

Signup on [XetHub](https://xethub.com/user/sign_up) and obtain
a username and access token. You should write this down.

There are three ways to authenticate with XetHub:

### Command Line

```bash
xet login -e <email> -u <username> -p <personal_access_token>
```
Xet login will write authentication information to `~/.xetconfig`

### Environment Variable
Environment variables may be sometimes more convenient:
```
export XET_USER_EMAIL = <email>
export XET_USER_NAME = <username>
export XET_USER_TOKEN = <personal_access_token>
```

### In Python
Finally if in a notebook environment, or a non-persistent environment,
we also provide a method to authenticate directly from Python. Note that
this must be the first thing you run before any other operation:
```python
import pyxet
pyxet.login(<username>, <personal_access_token>, <email>)
```

# Usage For Jupyter Notebooks

For Jupyter notebooks, run the following command to load the extension
```
%load_ext xetcache
```

If you are caching XetHub, you need to run:
```
import xetcache
xetcache.set_xet_project([give a project name here])
```

After which adding the following line to the top of a cell
```
%%xetmemo input=v1,v2 output=v3,v4
```
will cache the specified output variables (v3,v4 here) each time it is called.
If called later with the same input values for v1,v2, the cached value is
returned and not reevaluated. The cache is persistent across Python runs.

# Usage For Function Caching

If you are caching XetHub, you need to run:
```
import xetcache
xetcache.set_xet_project([give a project name here])
```

To cache the output of a function:
```
from xetcache import xetmemo

@xetmemo
def slow_function(stuff):
    ...
```
This will caches the function outputs each time it is called.
If called later with the same inputs , the cached value is returned
and not reevaluated. This is persistent across Python runs.

# Performance 
For performance reasons, only functions which take more than 3
seconds (configurable from `xetcache.config.set_runtime_threshold`) will be
cached. 

If you want to cache the result always in a Jupyter notebook cell,
add always=True to the cell magic line. ex:
```
%%xetmemo input=v1,v2 output=v3,v4 magic=True
```

And if you want to cache the result always for a function,
replace `xetmemo` with `xetmemo_always`.
```
from xetcache import xetmemo_always

@xetmemo_always
def slow_function(stuff):
    ...
```

# License
[BSD 3](LICENSE)


