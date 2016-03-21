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
import time

import Xlib.display
import ewmh
import pyatspi
from Xlib import X
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

    window_names = []
    window_names.append(wm.getWmName(active_win))

    wm_name = active_win.get_full_property(display.get_atom('WM_NAME'), X.AnyPropertyType)
    debug('WM_NAME original %s' % wm_name.value)
    wm_name = _from_compound_text(wm_name.value)
    debug('WM_NAME decoded %s' % wm_name)
    if wm_name not in window_names:
        window_names.append(wm_name)

    gdk_display = Gdk.Display.get_default()
    gdk_window = GdkX11.X11Window.foreign_new_for_display(gdk_display, active_win.id)

    gdk_frame_rect = gdk_window.get_frame_extents()
    gdk_frame_rect = (gdk_frame_rect.x, gdk_frame_rect.y,
                      gdk_frame_rect.width, gdk_frame_rect.height)
    gdk_geom_rect = gdk_window.get_geometry()

    debug('active window %s' % (window_names,))
    debug('active window id %s' % active_win.id)

    match = []
    for win in _atspi_windows():
        atspi_name = str(win)
        matched_names = [name
                         for name in window_names
                         if atspi_name.endswith('| %s]' % name)]
        debug('win with name %s, matched %s' % (atspi_name, matched_names))
        if matched_names and _geometry_match(win, gdk_frame_rect, gdk_geom_rect):
            match.append(win)

    if not match:
        debug('no atspi window matching "%s"' % window_names)
        return None, None

    if len(match) > 1:
        debug('too many atspi windows matching "%s"' % window_names)
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


def _from_compound_text(text):
    # FIXME: not a real COMPOUND_TEXT parser.
    #
    # Here is an example string taken from Konversation WM_NAME:
    #
    # Freenode \x1b%G\xe2\x80\x93\x1b%@ Konversation
    #
    # In the terms used by compound text spec, those special sequences are:
    #
    # \x1b%G - 01/11 02/05 04/07
    # \x1b%@ - 01/11 02/05 04/00
    #
    # An image(!) embedded on this doc confirms that these sequences start/stop UTF-8
    # mode:
    #
    # ftp://ftp.riken.jp/X11/XFree86/4.4.0/doc/HTML/ctext.html#7.%20The%20UTF-8%20encoding
    #
    # I don't know why this can't be found in any more official doc...
    #
    # Anyway, this method should really delegate to XmbTextListToTextProperty, but that
    # means adding some C into this module since no library we currently use has
    # appropriate bindings for it.
    #
    # So for now, I'll just assume that, on modern systems, in practice this UTF-8
    # start/stop is the only sequence that matters. Just strip it and the caller can
    # interpret the name as utf-8.
    text = text.replace('\x1b%G', '')
    text = text.replace('\x1b%@', '')
    return text
