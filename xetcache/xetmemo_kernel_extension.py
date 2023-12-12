import os
import time

from .util import hash_anything, probe_memo, store_memo
from .config import get_memo_path, get_runtime_threshold
from IPython.core.magic import Magics, magics_class, cell_magic


@magics_class
class XMemoMagics(Magics):
    """Memoization for data science tasks

       %load_ext xetcache

    to load the extension
    """

    def __init__(self, *args, **kwargs):
        print(self.xetmemo.__doc__)
        memopath = get_memo_path()
        print(f"Memoizing to {memopath}")
        super().__init__(*args, **kwargs)

    @cell_magic
    def xetmemo(self, line, cell):
        '''
        Usage:

           %%xetmemo input=v1,v2 output=v3,v4

        Caches the specified output variables each time it is called.
        If called later with the same inputs , the cached value is returned
        and not reevaluated. This is persistent across Python runs.

        Any content changes to the input input variables, or cell code will
        force reevaluation of the cell. Otherwise the outputs will simply be
        retrieved from the memo.

        This memo is persistent across Python processes and if XetHub is used
        see `xetcache.set_xet_project`, can be shared with others.

        For performance reasons, only functions which take more than 3
        seconds (configurable from config.set_runtime_threshold) will be 
        cached. "always=True" can be added to the xetmemo arguments to
        ignore the runime and to always cache

           %%xetmemo input=v1,v2 output=v3,v4 always=True

        Note that inputs can be anything picklable including functions.

        A key parameter can be added to group the stored objects together.
        Objects stored with one key will not be retrievable with a different
        key

           %%xetmemo input=v1,v2 output=v3,v4 always=True key=experiment1

        Also see the `xetcache.xetmemo` decorator for a version that can be
        used as a function decorator
        '''
        # parse the argument list
        args = line.strip().split(' ')
        inputvars = []
        outputvars = []
        ip = self.shell
        always = False
        key = None

        for arg in args:
            k, v = arg.split('=')
            if k == 'input':
                inputvars = [x.strip() for x in v.split(',')]
            elif k == 'output':
                outputvars = [x.strip() for x in v.split(',')]
            elif k == 'always':
                always = (v.strip() == 'True')
            elif k == 'key':
                key = v.strip()
            else:
                raise RuntimeError(f'Unexpected xmemo key type {k}')

        # we hash the xetmemo line, and the contents of the cell
        # and all the variables in the input line
        inputhashes = [hash_anything(line), hash_anything(cell)]
        for i in inputvars:
            try:
                var = ip.ev(i)
            except Exception as e:
                print(f"Unable to read variable {i}. Error {e}")
                return

            try:
                h = hash_anything(var)
            except Exception as e:
                print(f"Unable to hash variable {i}. Error {e}")
                return
            inputhashes.append(h)

        # Then we hash the list of hashes and use that as the filename
        inputhashstr = hash_anything(inputhashes)

        memopath = get_memo_path()
        runtime_threshold = get_runtime_threshold()
        try:
            retrieved_vals = probe_memo(memopath, inputhashstr, key)
            if retrieved_vals is not None:
                keys = retrieved_vals.keys()
                print(f"Retrieving variables {list(keys)}")
                for k, v in retrieved_vals.items():
                    ip.user_ns[k] = v
                return
        except Exception as e:
            print(f"Unable to load from memo from {memopath}: {e}")
            print("Executing the cell normally")

        start_time = time.time()
        ret = ip.run_cell(cell)
        elapsed_time = time.time() - start_time

        if ret.success and (always or elapsed_time > runtime_threshold):
            try:
                storedict = {}
                for v in outputvars:
                    if v not in ip.user_ns:
                        print(f"{v} not found in scope. Error in specification. Not memoizing.")
                        return
                    storedict[v] = ip.user_ns[v]
                store_memo(memopath, inputhashstr, storedict, key)
            except Exception as e:
                print(f"Unable to write memo file to {memopath}: {e}")


def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(XMemoMagics)
