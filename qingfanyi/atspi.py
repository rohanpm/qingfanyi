# coding=utf-8
import pyatspi
import time

from gi.repository import Gdk
from gi.repository.Atspi import StateType
from pyatspi.utils import stateToString
from pyatspi.state import STATE_SHOWING
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
        time.sleep(0.05)
        return active_window(attempts-1)

    gdk_window = Gdk.Screen.get_default().get_active_window()
    if not gdk_window:
        debug('no active gdk window.')
        return maybe_fail()

    gdk_frame_rect = gdk_window.get_frame_extents()
    gdk_frame_rect = (gdk_frame_rect.x, gdk_frame_rect.y,
                      gdk_frame_rect.width, gdk_frame_rect.height)
    gdk_geom_rect = gdk_window.get_geometry()

    atspi_windows = _atspi_active_windows()
    matching_windows = [x for x in atspi_windows
                        if _geometry_match(x, gdk_frame_rect, gdk_geom_rect)]

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
                debug('    ACTIVE')
    return out


def _geometry_match(accessible_window, frame, geom):
    # Observations:
    #
    # - the width/height of getExtents(0) and getExtents(1) has always been consistent
    #
    # - gedit: getExtents(0) is exactly equal to frame
    #          getExtents(1) is not equal to frame or geom
    #
    # - firefox: getExtents(0) is not equal to frame or geom
    #            getExtents(1) is exactly equal to geom
    #
    # It seems possible that implementors may not agree on what getExtents is supposed
    # to return...
    component = accessible_window.queryComponent()
    extents0 = component.getExtents(0)
    extents0 = tuple(extents0)
    extents1 = component.getExtents(1)
    extents1 = tuple(extents1)

    debug(('\n'
           ' EXTENTS 0 - %s\n'
           ' EXTENTS 1 - %s\n'
           ' FRAME     - %s\n'
           ' GEOM      - %s\n') % (extents0, extents1, frame, geom))

    # match gedit case
    if extents0 == frame:
        debug(' MATCH by frame')
        return True

    # match firefox case
    if extents1 == geom:
        debug(' MATCH by geom')
        return True


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
