# coding=utf-8
import datetime
import os
import sys

_DEBUG = 'QFY_DEBUG' in os.environ and os.environ['QFY_DEBUG'] == '1'


def debug(msg):
    """
    Prints a message to stderr, only if QFY_DEBUG environment variable is set to 1.

    :param msg: a string or object to be converted to string.  (Should not end with
                newline)
    """
    if _DEBUG:
        if hasattr(msg, '__call__'):
            msg = msg()
        sys.stdout.flush()
        s = 'debug: %s: %s\n' % (datetime.datetime.now(), msg)
        if isinstance(s, unicode):
            s = s.encode('utf-8', errors='replace')
        sys.stderr.write(s)
        sys.stderr.flush()
