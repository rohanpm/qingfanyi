# coding=utf-8
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
        sys.stdout.flush()
        sys.stderr.write('debug: %s\n' % msg)
        sys.stderr.flush()
