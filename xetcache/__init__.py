import functools
import time

from .xetmemo_kernel_extension import load_ipython_extension
from .config import get_memo_path, set_memo_path, get_runtime_threshold, \
        set_runtime_threshold, login, set_xet_project


def xetmemo(obj):
    '''
    xetmemo decorator.

    Caches the function outputs each time it is called.
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.

    Any content changes to the input input variables, or cell code will
    force reevaluation of the cell. Otherwise the outputs will simply be
    retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    For performance reasons, only functions which take more than 3
    seconds (configurable from config.set_runtime_threshold) will be
    cached. Use `xetmemo_always` to always cache ignoring the runtime.

    Also see the `%%xetmemo` cell magic for a version that can be
    for Jupyter notebook cells
    '''
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        memopath = get_memo_path()
        from .util import hash_anything, probe_memo, store_memo
        inputhashstr = hash_anything([args, kwargs])
        try:
            retrieved_vals = probe_memo(memopath, inputhashstr)
            if retrieved_vals is not None:
                if "RETVAL" in retrieved_vals:
                    return retrieved_vals["RETVAL"]
        except Exception as e:
            print(f"Unable to load from memo from {memopath}: {e}")
            print("Executing normally")

        start_time = time.time()
        ret = obj(*args, **kwargs)
        elapsed_time = time.time() - start_time
        if elapsed_time > get_runtime_threshold():
            try:
                store_memo(memopath, inputhashstr, {"RETVAL": ret})
            except Exception as e:
                print(f"Unable to write memo file to {memopath}: {e}")
        return ret
    return memoizer


def xetmemo_always(obj):
    '''
    xetmemo decorator.

    Caches the function outputs each time it is called.
    If called later with the same inputs , the cached value is returned
    and not reevaluated. This is persistent across Python runs.

    Any content changes to the input input variables, or cell code will
    force reevaluation of the cell. Otherwise the outputs will simply be
    retrieved from the memo.

    This memo is persistent across Python processes and if XetHub is used
    see `xetcache.set_xet_project`, can be shared with others.

    Use `xetmemo` to only cache functions which take more than 3
    seconds to run.

    Also see the `%%xetmemo` cell magic for a version that can be
    for Jupyter notebook cells
    '''
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        memopath = get_memo_path()
        from .util import hash_anything, probe_memo, store_memo
        inputhashstr = hash_anything([args, kwargs])
        try:
            retrieved_vals = probe_memo(memopath, inputhashstr)
            if retrieved_vals is not None:
                if "RETVAL" in retrieved_vals:
                    return retrieved_vals["RETVAL"]
        except Exception as e:
            print(f"Unable to load from memo from {memopath}: {e}")
            print("Executing normally")

        ret = obj(*args, **kwargs)
        try:
            store_memo(memopath, inputhashstr, {"RETVAL": ret})
        except Exception as e:
            print(f"Unable to write memo file to {memopath}: {e}")
        return ret
    return memoizer
