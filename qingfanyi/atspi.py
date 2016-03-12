# coding=utf-8
import pyatspi
import time

from gi.repository import Gdk

from qingfanyi import debug


def active_window(attempts=8):
    """
    :return: a tuple of the AT-SPI handle and GDK handle for the currently active window,
             or (None, None)

    Internally, this method tries to deal with several problems which have been
    observed when querying for the active window:

    - AT-SPI info sometimes is incorrect, then correct if queried again a moment later
    - AT-SPI sometimes claims more than one active window
    - AT-SPI and GDK sometimes disagree on which window is active
    """

    def maybe_fail():
        if attempts <= 0:
            debug(' cannot find active window after several attempts')
            return None, None
        debug(' try again to find active window')
        time.sleep(0.1)
        return active_window(attempts-1)

    gdk_window = Gdk.Screen.get_default().get_active_window()
    if not gdk_window:
        debug('no active gdk window.')
        return maybe_fail()

    gdk_rect = gdk_window.get_frame_extents()
    gdk_rect = (gdk_rect.x, gdk_rect.y, gdk_rect.width, gdk_rect.height)

    atspi_windows = _atspi_active_windows()
    matching_windows = [x for x in atspi_windows if _geometry_match(x, gdk_rect)]

    if not matching_windows:
        debug('no active atspi window matching GDK geometry')
        return maybe_fail()

    if len(matching_windows) > 1:
        debug('too many matching atspi windows!')
        return maybe_fail()

    return matching_windows[0], gdk_window

def _atspi_active_windows():
    """
    :return: all windows AT-SPI claims are active (there can be more than one)
    """
    desktop = pyatspi.Registry.getDesktop(0)
    out = []
    for app in desktop:
        for window in app:
            state = window.getState()
            debug('  window %s state %s' % (window, state.states))
            if state.contains(pyatspi.STATE_ACTIVE):
                out.append(window)
    return out


def _geometry_match(accessible_window, gdk_rect):
    (x, y, w, h) = accessible_window.queryComponent().getExtents(0)
    return (x, y, w, h) == gdk_rect


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
