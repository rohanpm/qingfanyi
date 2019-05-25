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
from queue import Full

from gi.repository import Keybinder
from gi.repository import Gtk

from qingfanyi import debug


def run(queue):
    keystr = "<Ctrl><Alt>z"
    Keybinder.init()
    assert Keybinder.bind(keystr, _on_shortcut, queue)
    debug('keybinder active')
    Gtk.main()


def _on_shortcut(event, queue):
    debug('shortcut %s' % event)
    try:
        queue.put_nowait(event)
    except Full:
        # this means earlier shortcut is still being processed
        debug('  dropped shortcut')