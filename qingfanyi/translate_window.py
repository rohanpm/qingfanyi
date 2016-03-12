# coding=utf-8
from gi.repository import Gtk
from gi.repository import GdkPixbuf

from qingfanyi import debug

class TranslateWindow(Gtk.Window):
    def __init__(self, snapshot):
        super(TranslateWindow, self).__init__(Gtk.WindowType.POPUP)

        (window_x, window_y, width, height) = snapshot.geometry
        src_pb = snapshot.pixbuf

        copy_pb = []
        for m in snapshot.matches:
            (x, y, w, h) = m.rect
            x -= window_x
            y -= window_y
            rect = (x, y, w, h)
            sub = src_pb.new_subpixbuf(*rect)
            if sub:
                sub = sub.copy()
                copy_pb.append((sub, rect))

        mod = src_pb.composite_color_simple(width, height, GdkPixbuf.InterpType.NEAREST,
                                            127, 2, 0, 0)

        for (pb, rect) in copy_pb:
            (x, y, w, h) = rect
            pb.copy_area(0, 0, w, h, mod, x, y)

        img = Gtk.Image.new_from_pixbuf(mod)
        img.show()

        debug('show image: %s %s' % (img, mod))

        self.connect('button-release-event', self.on_button_released)
        #img.connect('button-release-event', self.on_button_released)
        self.add(img)
        self.set_resizable(False)
        self.set_decorated(False)
        self.move(window_x, window_y)
        self.resize(width, height)


    def on_button_released(self, widget, event):
        debug('button released: %s' % event)
        self.destroy()
