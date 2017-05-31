##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


import shutil
import os
import doctest

def rmtree (path):
    """
    A variant of shutil.rmtree which tries hard to be successful
    On windows shutil.rmtree aborts when it tries to delete a
    read only file.
    This tries to chmod the file to writeable and retries before giving up.

    Also it tries to remove symlink itself if a symlink as passed as
    path argument.
    >>> from tempfile import mkdtemp

    Let's make a directory ...

    >>> d = mkdtemp()

    and make sure it is actually there

    >>> os.path.isdir (d)
    1

    Now create a file ...

    >>> foo = os.path.join (d, 'foo')
    >>> _ = open (foo, 'w').write ('huhu')
    >>> bar = os.path.join (d, 'bar')
    >>> os.symlink(bar, bar)

    and make it unwriteable

    >>> os.chmod (foo, 256) # 0400

    rmtree should be able to remove it:

    >>> rmtree (d)

    and now the directory is gone

    >>> os.path.isdir (d)
    0

    Let's make a directory ...

    >>> d = mkdtemp()

    and make sure it is actually there

    >>> os.path.isdir (d)
    1

    Now create a broken symlink ...

    >>> foo = os.path.join (d, 'foo')
    >>> os.symlink(foo + '.not_exist', foo)

    rmtree should be able to remove it:

    >>> rmtree (foo)

    and now the directory is gone

    >>> os.path.isdir (foo)
    0

    cleanup directory

    >>> rmtree (d)

    and now the directory is gone

    >>> os.path.isdir (d)
    0
    """
    def retry_writeable (func, path, exc):
        if func is os.path.islink:
            os.unlink(path)
        elif func is os.lstat:
            if not os.path.islink(path):
                raise
            os.unlink(path)
        else:
            os.chmod(path, 0o600)
            func(path)

    shutil.rmtree (path, onerror = retry_writeable)

def test_suite():
    return doctest.DocTestSuite()

if "__main__" == __name__:
    doctest.testmod()

