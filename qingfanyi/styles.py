# coding=utf-8
from gi.repository import Gtk, Gdk


def init():
    provider = Gtk.CssProvider.new()
    provider.load_from_data(_DATA)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


# https://developer.gnome.org/gtk3/stable/GtkCssProvider.html
_DATA = '''

#popup_window {
  border-style: solid;
  border-color: black;
  border-width: 1px;
}

GtkLabel#match {
  font-size: xx-large;
}

GtkLabel#main_pinyin {
  font-weight: bold;
}

'''