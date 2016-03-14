# coding=utf-8

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
