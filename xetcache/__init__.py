import functools
import time

from .xetmemo_kernel_extension import load_ipython_extension
from .config import get_memo_path, set_memo_path, get_runtime_threshold, \
        set_runtime_threshold, login, set_xet_project


class xetmemo(object):
    '''
    xetmemo decorator.

    Use as
    ```
    @xetmemo
    def slowfunction(arg1, arg2):
       ...

    # Stores with a key
    @xetmemo(key="hello")
    def slowfunction(arg1, arg2):
       ...

    # This will always cache irrespective of runtime
    @xetmemo(always=True)
    def slowfunction(arg1, arg2):
       ...
    ```

    Caches the function outputs each time it is called.
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.

    The optional key parameter is a string that is used to group the stored
    objects together.  Objects stored with one key will not be retrievable with
    a different key. 

    Any content changes to the input input variables, or cell code will
    force reevaluation of the cell. Otherwise the outputs will simply be
    retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    By default caching will only take place if the function takes more than 3
    seconds to run. always=True can be used to force caching.

    Also see the `%%xetmemo` cell magic for a version that can be
    for Jupyter notebook cells
    '''

    def __init__(self, key=None, always=None):
        self.obj = None
        self.key = None
        self.always = False

        if callable(key) and always is None:
            # used without parameters
            self.obj = key
        else:
            self.key = key
            self.always = always

    def __call__(self, *args, **kwargs):
        if self.obj is not None:
            # used without parameters
            obj = self.obj
        else:
            obj = args[0]

        key = self.key
        always = self.always

        @functools.wraps(obj)
        def memoizer(*args, **kwargs):
            memopath = get_memo_path()
            from .util import hash_fn, hash_anything, probe_memo, store_memo
            inputhashstr = hash_anything([hash_fn(obj), args, kwargs])
            try:
                retrieved_vals = probe_memo(memopath, inputhashstr, key)
                if retrieved_vals is not None:
                    if "RETVAL" in retrieved_vals:
                        return retrieved_vals["RETVAL"]
            except Exception as e:
                print(f"Unable to load from memo from {memopath}: {e}")
                print("Executing normally")

            start_time = time.time()
            ret = obj(*args, **kwargs)
            elapsed_time = time.time() - start_time
            if always or elapsed_time > get_runtime_threshold():
                try:
                    store_memo(memopath, inputhashstr, {"RETVAL": ret}, key)
                except Exception as e:
                    print(f"Unable to write memo file to {memopath}: {e}")
            return ret

        if self.obj is not None:
            # used without parameters
            # args are the actual function call
            # and we have to run it now
            obj = self.obj
            return memoizer(*args, **kwargs)
        else:
            return memoizer


def xeteval(key_or_f, *args, **kwargs):
    """
    Caches the result of a function call:
    ```
    def slowfn(x):
        ..do stuff..

    # caches the call to slowfn with argument x
    xeteval(slowfn, x)

    # Stores with a key
    xeteval("key", slowfn, x)
    ```
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.

    The optional key parameter is a string that is used to group the stored
    objects together.  Objects stored with one key will not be retrievable with
    a different key. 

    Any changes to any of the arguments will force reevaluation of the cell.
    Otherwise the outputs will simply be retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    The cache will only be used if the function take more than 3
    seconds to run.

    See `xeteval_always` to always cache ignoring function runtime
    and `xetmemo` for a decorator version.
    """
    if callable(key_or_f):
        return _xeteval_impl(None, key_or_f, False, *args, **kwargs)
    else:
        key = key_or_f
        f = args[0]
        args = args[1:]
        return _xeteval_impl(key, f, False, *args, **kwargs)


def xeteval_always(key_or_f, *args, **kwargs):
    """
    Caches the result of a function call:
    ```
    def slowfn(x):
        ..do stuff..

    # caches the call to slowfn with argument x
    xeteval_always(slowfn, x)

    # Stores with a key
    xeteval_always("key", slowfn, x)
    ```
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.

    The optional key parameter is a string that is used to group the stored
    objects together.  Objects stored with one key will not be retrievable with
    a different key. 

    Any changes to any of the arguments will force reevaluation of the cell.
    Otherwise the outputs will simply be retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    See `xeteval` to only cache long running functions
    and `xetmemo` for a decorator version.
    """
    if callable(key_or_f):
        return _xeteval_impl(None, key_or_f, True, *args, **kwargs)
    else:
        key = key_or_f
        f = args[0]
        args = args[1:]
        return _xeteval_impl(key, f, True, *args, **kwargs)

def _xeteval_impl(key, f, always, *args, **kwargs):
    """
    Caches the function call f(*args,  **kwargs)
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.
    The key parameter is a string that is used to group the stored objects
    together.  Objects stored with one key will not be retrievable with a
    different key. 

    Any changes to any of the arguments will force reevaluation of the cell.
    Otherwise the outputs will simply be retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    The cache will only be used if the function take more than 3
    seconds to run.

    See `xeteval` for a version without a key
    See `xetmemo` for a decorator version.
    """
    memopath = get_memo_path()
    from .util import hash_fn, hash_anything, probe_memo, store_memo
    inputhashstr = hash_anything([hash_fn(f), args, kwargs])
    try:
        retrieved_vals = probe_memo(memopath, inputhashstr, key)
        if retrieved_vals is not None:
            if "RETVAL" in retrieved_vals:
                return retrieved_vals["RETVAL"]
    except Exception as e:
        print(f"Unable to load from memo from {memopath}: {e}")
        print("Executing normally")

    start_time = time.time()
    ret = f(*args, **kwargs)
    elapsed_time = time.time() - start_time
    if always or elapsed_time > get_runtime_threshold():
        try:
            store_memo(memopath, inputhashstr, {"RETVAL": ret}, key)
        except Exception as e:
            print(f"Unable to write memo file to {memopath}: {e}")
    return ret


try:
    from IPython import get_ipython
    ip = get_ipython()
    load_ipython_extension(ip)
except:
    pass
