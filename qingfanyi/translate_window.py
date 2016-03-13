# coding=utf-8
from gi.repository import Gtk, Gdk, GLib, GObject
from gi.repository import GdkPixbuf

from qingfanyi import debug


class TranslateWindow(Gtk.Window):
    __gsignals__ = {
        'lookup-requested': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                             (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, snapshot):
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.current_match_index = None
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
        GLib.idle_add(self.process_matches)

    def relative_rect(self, match):
        (window_x, window_y, _, _) = self.snapshot.geometry
        (x, y, w, h) = match.rect
        x -= window_x
        y -= window_y
        return x, y, w, h

    def invert(self, rect):
        (x, y, w, h) = rect
        sub = self.pixbuf.new_subpixbuf(*rect).copy()
        pix = sub.get_pixels()
        alpha = sub.get_has_alpha()
        bytes_per_pixel = 4 if alpha else 3
        stride = sub.get_rowstride()
        bytes_total = stride*h

        npix = bytearray(bytes_total)
        for i in range(h):
            for j in range(0, w*bytes_per_pixel, bytes_per_pixel):
                npix[i*stride + j]     = 255 - ord(pix[i*stride + j])
                npix[i*stride + j + 1] = 255 - ord(pix[i*stride + j + 1])
                npix[i*stride + j + 2] = 255 - ord(pix[i*stride + j + 2])
                if alpha:
                    npix[i*stride + j + 3] = 255

        bytes = GLib.Bytes.new(npix)
        debug('have bytes: %s for rect: %s' % (bytes.get_size(), rect))
        sub = GdkPixbuf.Pixbuf.new_from_bytes(
            bytes,
            GdkPixbuf.Colorspace.RGB,
            sub.get_has_alpha(),
            sub.get_bits_per_sample(),
            sub.get_width(),
            sub.get_height(),
            sub.get_rowstride()
        )
        sub.copy_area(0, 0, w, h, self.pixbuf, x, y)
        self.img.set_from_pixbuf(self.pixbuf)


    def set_current_match(self, idx, match):
        if self.current_match_index == idx:
            return

        if self.current_match_index is not None:
            prev_match = self.snapshot.matches[self.current_match_index]
            prev_rect = self.relative_rect(prev_match)
            self.invert(prev_rect)

        self.current_match_index = idx
        rect = self.relative_rect(match)
        self.invert(rect)
        self.emit('lookup-requested', match)

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
            self.navigate(-len(self.snapshot.matches) / 10)
        elif key == Gdk.KEY_Down:
            self.navigate(len(self.snapshot.matches) / 10)
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

        size = len(self.snapshot.matches)
        if idx >= size:
            idx -= size
        elif idx < 0:
            idx += size

        self.set_current_match(idx, self.snapshot.matches[idx])

    def lookup_match(self, event):
        (window_x, window_y, _, _) = self.snapshot.geometry
        event_x = event.x
        event_y = event.y

        i = 0
        for m in self.snapshot.matches:
            (x, y, w, h) = m.rect
            x -= window_x
            y -= window_y
            if x <= event_x < x+w and y <= event_y < y+h:
                return m, i
            i += 1

        return None, None

    def process_matches(self):
        self.set_can_default(True)
        self.grab_default()
        self.img.set_can_focus(True)
        self.img.grab_focus()

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