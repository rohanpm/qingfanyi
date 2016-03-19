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
from gi.repository import GObject

from qingfanyi import debug
from qingfanyi.popup_window import PopupWindow


class PopupManager(GObject.GObject):
    """
    Manager class connecting translation window with popups.

    Current design allows only one popup at a time.
    """

    def __init__(self, translation_window):
        translation_window.connect('lookup-requested', self.popup_for_match)
        self.active = None

    def popup_for_match(self, sender, match):
        debug('would popup for %s' % match)
        if self.active:
            self.active.destroy()
        self.active = self.make_active(sender, match)

    def unset_active(self):
        debug('unset active')
        self.active = None

    def make_active(self, sender, match):
        win = PopupWindow(sender, match)
        win.connect('hide', lambda *_: self.unset_active())
        win.show()
        return win
