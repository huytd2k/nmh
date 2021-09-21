from contextlib import contextmanager
import os


@contextmanager
def cd(newdir):  # pylint: disable=C0103
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield newdir
    finally:
        os.chdir(prevdir)
