# coding=utf-8
from gi.repository import Gtk, GLib

from qingfanyi import debug


class PopupWindow(Gtk.Window):
    def __init__(self, match):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)

        (x, y, w, h) = match.rect
        self.move(x + w/2, y + h + 4)

        layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 4)

        label = Gtk.Label.new()
        label.set_markup(_markup(match))
        label.show()
        layout.pack_start(label, True, False, 0)

        layout.show()
        self.add(layout)

        debug('should popup for %s' % match)

def _markup(match):
    # https://developer.gnome.org/pango/stable/PangoMarkupFormat.html#PangoMarkupFormat
    out = []
    out.append('<span size="xx-large">%s</span>' % GLib.markup_escape_text(match.text))
    out.append('')

    for record in match.records:
        out.append('<b>%s</b>' % GLib.markup_escape_text(record.pinyin))
        for en in record.en_US:
            out.append('• %s' % GLib.markup_escape_text(en))
        out.append('')

    out.pop()
    return '\n'.join(out)
