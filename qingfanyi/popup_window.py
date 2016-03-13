# coding=utf-8
from gi.repository import Gtk, GLib

from qingfanyi import debug


class PopupWindow(Gtk.Window):
    def __init__(self, match):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)

        self.set_name('popup_window')

        # FIXME: any way to do this with CSS?  Can't make it work...
        self.set_border_width(5)

        self.set_size_request(80, -1)

        (x, y, w, h) = match.rect
        self.move(x + w/2, y + h + 4)

        layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 4)

        _add_labels(layout, match)

        layout.show()
        self.add(layout)

        debug('should popup for %s' % match)

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
            label = Gtk.Label('• %s' % en)
            label.set_name('en_US')
            add(label)

