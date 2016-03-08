# coding=utf-8
import pyatspi

from qingfanyi import debug


def active_window():
    """
    :return: the AT-SPI handle for the currently active window, or None.
    """
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        for window in app:
            if window.getState().contains(pyatspi.STATE_ACTIVE):
                return window


def is_visible(accessible_object):
    """
    Returns true if accessible_object appears to be a visible component on the screen.

    Note that invisible components can have visible children.

    :param accessible_object: an AtSpi.Accessible
    """
    try:
        component = accessible_object.queryComponent()
        (w, h) = component.getSize()
        # anything smaller than (10,10) is invisible or too small to work with
        return w > 10 and h > 10
    except NotImplementedError:
        # not a component? not visible...
        debug('not a component: %s' % accessible_object)
        return False


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
    if is_visible(root):
        callback(root, level)

    for child in root:
        visit_visible(child, callback, level + 1)
