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
from gi.repository import Gtk, Gdk

from qingfanyi import debug


class PopupWindow(Gtk.Window):
    def __init__(self, parent, match):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)

        self.set_name('popup_window')

        # FIXME: any way to do this with CSS?  Can't make it work...
        self.set_border_width(5)

        self.set_size_request(80, -1)

        layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 4)

        _add_labels(layout, match)

        layout.show()
        self.add(layout)

        # Initially set a position near the match (at least so it's on the right monitor);
        # init_position is expected to make this better later
        (x, y, _, _) = match.rects[0]
        self.move(x, y)

        debug('should popup for %s' % match)

        def do_init_position(*_):
            self.init_position(parent, match)

        self.connect('size-allocate', do_init_position)

    def init_position(self, parent, match):
        self_w = self.get_allocated_width()
        self_h = self.get_allocated_height()

        screen = Gdk.Screen.get_default()
        monitor = screen.get_monitor_at_window(parent.get_window())
        debug('monitor %d' % monitor)
        monitor_rect = screen.get_monitor_geometry(monitor)
        (root_x, root_y, root_w, root_h) = (monitor_rect.x, monitor_rect.y,
                                            monitor_rect.width, monitor_rect.height)
        (mx, my, mw, mh) = match.rects[0]

        def adjust_x(val):
            debug('adjust x %s: root (%s .. %s)' % (val, root_x, root_x + root_w))
            if self_w >= root_w:
                return val
            while val + self_w > root_x + root_w:
                val -= 1
            while val < root_x:
                val += 1
            debug('adjust to %s' % val)
            return val

        # First try below.
        (x, y) = mx + mw/4, my + mh + 3
        if y + self_h < root_y + root_h:
            self.move(adjust_x(x), y)
            return

        # Then above.
        (x, y) = mx + mw/4, my - self_h - 3
        self.move(adjust_x(x), y)




def _add_labels(layout, match):
    debug('add labels')
    def add(l):
        l.show()
        l.set_alignment(0, 0)
        layout.pack_start(l, True, False, 0)

    # https://developer.gnome.org/pango/stable/PangoMarkupFormat.html#PangoMarkupFormat
    text_label = Gtk.Label(match.text)
    text_label.set_name('match')
    add(text_label)

    for record in match.records:
        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep.show()
        layout.pack_start(sep, True, False, 0)

        label = Gtk.Label(record.pinyin)
        label.set_name('main_pinyin')
        add(label)
        for en in record.en_US:
            label = Gtk.Label(u'• %s' % en)
            label.set_name('en_US')
            add(label)
