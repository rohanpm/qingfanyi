# coding=utf-8
# qingfanyi - Chinese to English translation tool
# Copyright (C) 2016 Rohan McGovern <rohan@mcgovern.id.au>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import datetime
import os
import sys

import gi
gi.require_version('Gtk', '3.0')

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
        s = 'debug: [%s] %s: %s\n' % (os.getpid(), datetime.datetime.now(), msg)
        if isinstance(s, bytes):
            s = str(s, 'utf-8', errors='replace')
        sys.stderr.write(s)
        sys.stderr.flush()
