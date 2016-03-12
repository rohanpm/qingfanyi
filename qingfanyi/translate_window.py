# coding=utf-8
from gi.repository import Gtk, GLib
from gi.repository import GdkPixbuf

from qingfanyi import debug

class TranslateWindow(Gtk.Window):
    def __init__(self, snapshot):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)

        self.snapshot = snapshot

        (window_x, window_y, width, height) = snapshot.geometry
        src_pb = snapshot.pixbuf
        self.pixbuf = src_pb.composite_color_simple(width, height,
                                                    GdkPixbuf.InterpType.NEAREST,
                                                    127, 2, 0, 0)

        self.img = Gtk.Image.new_from_pixbuf(self.pixbuf)
        self.img.show()

        self.connect('button-release-event', self.on_button_released)
        self.add(self.img)
        self.set_resizable(False)
        self.set_decorated(False)
        self.move(window_x, window_y)
        self.resize(width, height)

        GLib.idle_add(self.process_matches)


    def on_button_released(self, widget, event):
        debug('button released: %s' % event)
        self.destroy()


    def process_matches(self):
        (window_x, window_y, width, height) = self.snapshot.geometry

        copy_pb = []
        for m in self.snapshot.matches:
            (x, y, w, h) = m.rect
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

        self.img.set_from_pixbuf(self.pixbuf)