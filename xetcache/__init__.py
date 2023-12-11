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

    # Key the cache entries
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

        key = str(self.key)
        always = self.always

        @functools.wraps(obj)
        def memoizer(*args, **kwargs):
            memopath = get_memo_path()
            from .util import hash_anything, probe_memo, store_memo
            inputhashstr = hash_anything([args, kwargs])
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


def xeteval(f, *args, **kwargs):
    """
    Caches the function call f(*args,  **kwargs)
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.

    Any changes to any of the arguments will force reevaluation of the cell.
    Otherwise the outputs will simply be retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    The cache will only be used if the function take more than 3
    seconds to run.

    See `xeteval_with_key` to group caches with a key,
    and `xetmemo` for a decorator version.
    """
    return xeteval_with_key(None, f, *args, **kwargs)

def xeteval_with_key(key, f, *args, **kwargs):
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
    key = str(key)
    memopath = get_memo_path()
    from .util import hash_anything, probe_memo, store_memo
    inputhashstr = hash_anything([args, kwargs])
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
    if elapsed_time > get_runtime_threshold():
        try:
            store_memo(memopath, inputhashstr, {"RETVAL": ret}, key)
        except Exception as e:
            print(f"Unable to write memo file to {memopath}: {e}")
    return ret
