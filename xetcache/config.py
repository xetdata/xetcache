import os
import pyxet
_MEMOPATH = os.path.join(os.getcwd(), 'xmemo')
_RUNTIME_THRESHOLD_SEC = 3

def login(user, token, email=None, host=None):
    """
    Sets the active login credentials used to authenticate against Xethub
    """
    pyxet.login(user, token, email, host)


def get_memo_path():
    """
    Reads the current memo path
    """
    return _MEMOPATH


def set_memo_path(memopath):
    """
    Sets the current memo path
    """
    global _MEMOPATH
    _MEMOPATH = memopath

def get_runtime_threshold():
    """
    Reads the current runtime threshold in seconds. 
    Only functions or cells which run longer than this will be cached.
    """
    return _RUNTIME_THRESHOLD_SEC


def set_runtime_threshold(runtime_threshold_sec):
    """
    Reads the current runtime threshold in seconds. 
    Only functions or cells which run longer than this will be cached.
    """
    global _RUNTIME_THRESHOLD_SEC
    _RUNTIME_THRESHOLD_SEC = runtime_threshold_sec




def set_xet_project(project, private):
    """
    Uses Xethub as a cache. A cache repo will be automatically created
    for each new project.
    """
    reponame = project + '_cache'
    fs = pyxet.XetFS()
    username = fs.get_username()
    repopath = f"{username}/{reponame}"
    haspath = False
    try:
        fs.stat(f"{repopath}/main")
        haspath = True
    except:
        pass

    if not haspath:
        print(f"Creating new repository at xet://{repopath}")
        fs.make_repo(f"xet://{repopath}", private=private)

    set_memo_path(f"xet://{username}/{reponame}/main")


