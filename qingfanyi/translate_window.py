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
from gi.repository import Gtk, Gdk, GLib, GObject
from gi.repository import GdkPixbuf

from qingfanyi import debug
from qingfanyi.geom import rect_within


class TranslateWindow(Gtk.Window):
    __gsignals__ = {
        'lookup-requested': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                             (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, snapshot):
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.current_match_index = None
        self.matches = []
        self.set_name('translate_window')
        self.set_decorated(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_title('qingfanyi')

        self.snapshot = snapshot

        (window_x, window_y, width, height) = snapshot.geometry
        src_pb = snapshot.pixbuf
        self.pixbuf = src_pb.composite_color_simple(width, height,
                                                    GdkPixbuf.InterpType.NEAREST,
                                                    127, 2, 0, 0)

        self.img = Gtk.Image.new_from_pixbuf(self.pixbuf)
        self.img.show()

        self.connect('button-release-event', self.on_button_released)
        self.connect('key-press-event', self.on_key_pressed)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.add(self.img)
        self.set_resizable(False)
        self.set_decorated(False)
        self.move(window_x, window_y)
        self.resize(width, height)
        # TODO: test if this is needed!
        GLib.idle_add(self.focus_in)

    def add_match(self, sender, match):
        # Only accept the match if all of its rects are within our geometry
        for rect in match.rects:
            if not rect_within(self.snapshot.geometry, rect):
                debug('rejecting match outside of window: %s' % match)
                return

        debug('adding match %s %s' % (match, sender))

        # Retain the current match if there is one.
        current = self.current_match

        self.matches.append(match)
        self.matches.sort(key=_match_sort_key)

        if current:
            for i in xrange(len(self.matches)):
                if self.matches[i] is current:
                    self.current_match_index = i
                    break

        self.redo_pixbuf()

    def relative_rect(self, rect):
        (window_x, window_y, _, _) = self.snapshot.geometry
        (x, y, w, h) = rect
        x -= window_x
        y -= window_y
        return x, y, w, h

    def invert(self, rect):
        (x, y, w, h) = rect
        sub = self.pixbuf.new_subpixbuf(*rect).copy()
        pix = sub.get_pixels()
        alpha = sub.get_has_alpha()
        istride = sub.get_rowstride()
        bytes_per_pixel = 4 if alpha else 3
        ostride = w*bytes_per_pixel
        bytes_total = ostride*h

        npix = bytearray(bytes_total)
        for i in range(h):
            for j in range(0, w*bytes_per_pixel, bytes_per_pixel):
                npix[i*ostride + j]     = 255 - ord(pix[i*istride + j])
                npix[i*ostride + j + 1] = 255 - ord(pix[i*istride + j + 1])
                npix[i*ostride + j + 2] = 255 - ord(pix[i*istride + j + 2])
                if alpha:
                    npix[i*ostride + j + 3] = 255

        bytes = GLib.Bytes.new(npix)
        debug('have bytes: %s for rect: %s' % (bytes.get_size(), rect))
        sub = GdkPixbuf.Pixbuf.new_from_bytes(
            bytes,
            GdkPixbuf.Colorspace.RGB,
            alpha,
            8,
            w,
            h,
            ostride
        )
        sub.copy_area(0, 0, w, h, self.pixbuf, x, y)
        self.img.set_from_pixbuf(self.pixbuf)

    def set_current_match(self, idx, match):
        if self.current_match_index == idx:
            return

        prev_match = self.current_match
        if prev_match:
            self.invert_for_match(prev_match)

        self.current_match_index = idx
        self.invert_for_match(match)

        self.emit('lookup-requested', match)

    def invert_for_match(self, match):
        for rect in match.rects:
            prev_rect = self.relative_rect(rect)
            self.invert(prev_rect)

    @property
    def current_match(self):
        if not self.current_match_index:
            return None
        return self.matches[self.current_match_index]

    def on_button_released(self, widget, event):
        debug('button released: %s' % ((event.button, event.x, event.y),))
        (match, idx) = self.lookup_match(event)
        if match:
            debug(' clicked on: %s' % match)
            self.set_current_match(idx, match)
        else:
            self.destroy()

    def on_key_pressed(self, widget, event):
        debug('key pressed: %s' % ((event.keyval, event.string),))

        key = event.keyval
        if key == Gdk.KEY_Left:
            self.navigate(-1)
        elif key == Gdk.KEY_Right:
            self.navigate(1)
        elif key == Gdk.KEY_Up:
            self.navigate(-len(self.matches) / 10)
        elif key == Gdk.KEY_Down:
            self.navigate(len(self.matches) / 10)
        elif event.string:
            self.destroy()

    def navigate(self, offset):
        idx = self.current_match_index
        if idx is None:
            if offset == 1:
                idx = 0
            else:
                idx = -1
        else:
            idx += offset

        size = len(self.matches)
        if idx >= size:
            idx -= size
        elif idx < 0:
            idx += size

        self.set_current_match(idx, self.matches[idx])

    def lookup_match(self, event):
        (window_x, window_y, _, _) = self.snapshot.geometry
        event_x = event.x
        event_y = event.y

        # There can be multiple matches, e.g. if user clicked on 你 from 你好, then
        # there will be a match for both 你 and 你好.
        # Currently we will always favor the leftmost and longest match.
        # We don't explicitly need code to do that, because they're already sorted that
        # way.

        i = 0
        for m in self.matches:
            for (x, y, w, h) in m.rects:
                x -= window_x
                y -= window_y
                if x <= event_x < x + w and y <= event_y < y + h:
                    return m, i
            i += 1

        return None, None

    def focus_in(self):
        self.set_can_default(True)
        self.grab_default()
        self.img.set_can_focus(True)
        self.img.grab_focus()

    def redo_pixbuf(self):
        debug('BEGIN redraw...')

        (window_x, window_y, width, height) = self.snapshot.geometry

        copy_pb = []
        for m in self.matches:
            for (x, y, w, h) in m.rects:
                x -= window_x
                y -= window_y
                rect = (x, y, w, h)
                sub = self.snapshot.pixbuf.new_subpixbuf(*rect)
                if sub:
                    sub = sub.copy()
                    copy_pb.append((sub, rect))

        for (pb, rect) in copy_pb:
            (x, y, w, h) = rect
            pb.copy_area(0, 0, w, h, self.pixbuf, x, y)

        match = self.current_match
        if match:
            self.invert_for_match(match)

        self.img.set_from_pixbuf(self.pixbuf)

        debug('END redraw')


def _match_sort_key(match):
    (x, y, w, h) = match.rects[0]
    return y, x, -len(match.text)
