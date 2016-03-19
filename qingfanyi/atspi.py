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

from pyatspi.state import STATE_SHOWING

from qingfanyi import debug

def _is_showing(accessible_object):
    return accessible_object.getState().contains(STATE_SHOWING)

def get_text_object(accessible_object):
    """
    :param accessible_object: an AtSpi.Accessible
    :return: the text interface for an accessible object if implemented, otherwise None.
    """
    try:
        return accessible_object.queryText()
    except NotImplementedError:
        return None


def visit_visible(root, callback, level=0):
    """
    Visit every visible object in a hierarchy and invoke a provided callback.

    :param root: an AtSpi.Accessible object
    :param callback: invoked for each visible object with two parameters: the object,
                     and the distance from root (e.g. 0 == root, 1 == child of root,
                     2 == grandchild ...)
    """
    debug('%s%s' % ('  '*level, root))
    if not _is_showing(root):
        debug('%s PRUNE' % ('  '*level))
        return

    callback(root, level)

    for child in root:
        visit_visible(child, callback, level + 1)
