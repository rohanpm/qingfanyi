# coding=utf-8
import time

import Xlib.display
import ewmh
import pyatspi
from gi.repository import Gdk, GLib, GdkX11

from qingfanyi import debug


def active_window(attempts=5):
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
            return _guess_active_window()
        debug(' try again to find active window')
        time.sleep(0.1)
        return active_window(attempts - 1)

    gdk_window = Gdk.Screen.get_default().get_active_window()
    if not gdk_window:
        debug('no active gdk window.')
        return maybe_fail()

    gdk_frame_rect = gdk_window.get_frame_extents()
    gdk_frame_rect = (gdk_frame_rect.x, gdk_frame_rect.y,
                      gdk_frame_rect.width, gdk_frame_rect.height)
    gdk_geom_rect = gdk_window.get_geometry()

    debug('for...')
    for win in _atspi_active_windows():
        debug('  iter')
        if _geometry_match(win, gdk_frame_rect, gdk_geom_rect):
            return win, gdk_window

    debug('no active atspi window matching GDK geometry')
    return maybe_fail()


def _guess_active_window():
    display = Xlib.display.Display()
    wm = ewmh.EWMH(display)
    active_win = wm.getActiveWindow()

    if not active_win:
        debug('no active window from ewmh')
        return None, None

    gdk_display = Gdk.Display.get_default()
    gdk_window = GdkX11.X11Window.foreign_new_for_display(gdk_display, active_win.id)

    gdk_frame_rect = gdk_window.get_frame_extents()
    gdk_frame_rect = (gdk_frame_rect.x, gdk_frame_rect.y,
                      gdk_frame_rect.width, gdk_frame_rect.height)
    gdk_geom_rect = gdk_window.get_geometry()

    window_name = wm.getWmName(active_win)
    debug('active window %s' % window_name)
    debug('active window id %s' % active_win.id)

    match = []
    for win in _atspi_windows():
        atspi_name = str(win)
        debug('win with name %s' % atspi_name)
        if _geometry_match(win, gdk_frame_rect, gdk_geom_rect) \
                and atspi_name.endswith('| ' + window_name + ']'):
            match.append(win)

    if not match:
        debug('no atspi window matching "%s"' % window_name)
        return None, None

    if len(match) > 1:
        debug('too many atspi windows matching "%s"' % window_name)
        return None, None

    return match[0], gdk_window


def _atspi_windows():
    desktop = pyatspi.Registry.getDesktop(0)
    for app in desktop:
        try:
            for window in app:
                yield window
        except GLib.Error as e:
            debug('error from app %s: %s' % (app, e))


def _atspi_active_windows():
    """
    :return: all windows AT-SPI claims are active (there can be more than one)
    """
    for window in _atspi_windows():
        state = window.getState()
        debug('  window %s state %s' % (window, state.states))
        if state.contains(pyatspi.STATE_ACTIVE):
            debug('    ACTIVE')
            yield window


def _geometry_match(accessible_window, frame, geom):
    # Observations: (using i3 as WM)
    #
    # - gedit: getExtents(0) is exactly equal to frame
    #          getExtents(1) is not equal to frame or geom
    #
    # - firefox: getExtents(0) is not equal to frame or geom
    #            getExtents(1) is exactly equal to geom
    #
    # - qtassistant-qt5: getExtents(0) (x,y) is almost equal to frame (x,y)
    #                    getExtents(1) (w,h) is exactly equal to geom (w,h)
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

    # match qt5 case
    (x0, y0, w0, h0) = extents0
    ( _,  _, wg, hg) = geom
    (fx, fy,  _,  _) = frame

    if (w0, h0) == (wg, hg) and abs(fx - x0) < 10 and abs(fy - y0) < 10:
        debug(' MATCH fuzzily')
        return True
