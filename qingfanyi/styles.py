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