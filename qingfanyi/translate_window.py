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
from qingfanyi.navigator import Navigator


class TranslateWindow(Gtk.Window):
    __gsignals__ = {
        'lookup-requested': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                             (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, snapshot, snapshot_matcher):
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

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

        self.unmatch_count = 0
        snapshot_matcher.connect('matches-found', self.add_matches)

        self.navigator = Navigator(self.snapshot.geometry)
        self.navigator.connect('current_match_changed', self.on_current_match_changed)

    def add_matches(self, sender, matches):

        def accept_match(match):
            # Only accept the match if all of its rects are within our geometry
            for rect in match.rects:
                if not rect_within(self.snapshot.geometry, rect):
                    debug('rejecting match outside of window: %s' % match)
                    return False
            return True

        matches = [m for m in matches if accept_match(m)]

        if not matches:
            self.unmatch_count += 1
            # If we previously have found something, and now we repeatedly cannot match
            # anything, then tell the sender to stop - probably it's wasting time
            # processing text far off the screen
            if self.navigator.matches and self.unmatch_count > 5:
                debug('sender keeps sending offscreen stuff. asking it to stop.')
                sender.stop()
            return

        self.unmatch_count = 0
        self.navigator.add_matches(matches)
        self.update_pixbuf_for_matches(matches)

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
        ostride = w * bytes_per_pixel
        bytes_total = ostride * h

        npix = bytearray(bytes_total)
        for i in range(h):
            for j in range(0, w * bytes_per_pixel, bytes_per_pixel):
                npix[i * ostride + j] = 255 - pix[i * istride + j]
                npix[i * ostride + j + 1] = 255 - pix[i * istride + j + 1]
                npix[i * ostride + j + 2] = 255 - pix[i * istride + j + 2]
                if alpha:
                    npix[i * ostride + j + 3] = 255

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

    def on_current_match_changed(self, _sender, prev_match, match):
        debug('match has changed from %s to %s' % (prev_match, match))

        if prev_match:
            self.invert_for_match(prev_match)

        if match:
            self.invert_for_match(match)
            self.emit('lookup-requested', match)

    def invert_for_match(self, match):
        for rect in match.rects:
            prev_rect = self.relative_rect(rect)
            self.invert(prev_rect)

    def on_button_released(self, widget, event):
        debug('button released: %s' % ((event.button, event.x, event.y),))
        found = self.navigator.set_current_match_by_point(event.x, event.y)
        if not found:
            # clicked somewhere with no match; close window
            self.destroy()

    def on_key_pressed(self, widget, event):
        debug('key pressed: %s' % ((event.keyval, event.string),))

        key = event.keyval
        if key == Gdk.KEY_Left:
            self.navigator.navigate_offset(-1)
        elif key == Gdk.KEY_Right:
            self.navigator.navigate_offset(1)
        elif key == Gdk.KEY_Up:
            self.navigator.navigate_offset(int(-len(self.navigator.matches) / 10))
        elif key == Gdk.KEY_Down:
            self.navigator.navigate_offset(int(len(self.navigator.matches) / 10))
        elif event.string:
            self.destroy()

    def focus_in(self):
        self.set_can_default(True)
        self.grab_default()
        self.img.set_can_focus(True)
        self.img.grab_focus()

    def update_pixbuf_for_matches(self, matches):
        debug('BEGIN redraw...')

        (window_x, window_y, width, height) = self.snapshot.geometry

        copy_pb = []

        current_match = self.navigator.current_match
        # Note: could improve to only process current_match if it overlaps.
        # But time savings are probably negligible.
        if current_match:
            matches.append(current_match)

        for m in matches:
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

        if current_match:
            debug('inverting current match - %s' % current_match)
            self.invert_for_match(current_match)

        self.img.set_from_pixbuf(self.pixbuf)

        debug('END redraw')


