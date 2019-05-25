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
from gi.repository import Gdk

from qingfanyi import debug
from qingfanyi.atspi import get_text_object, visit_visible
from qingfanyi.text import may_contain_chinese


class Snapshot(object):
    """This class represents a snapshot of a current window.

    On creation, it will grab and store:

    - geometry and screenshot of window
    - handles to text objects likely containing Chinese text

    This can take a few seconds.

    Notably, this class does _not_ parse the Chinese text or query text rects
    from the application, because that is too slow to be done synchronously.
    """
    def __init__(self, accessible_window, gdk_window):
        (_, _, w, h) = gdk_window.get_geometry()
        (_, x, y) = gdk_window.get_origin()

        self.geometry = (x, y, w, h)
        debug('taking snapshot of %s' % gdk_window)
        self.pixbuf = Gdk.pixbuf_get_from_window(gdk_window, 0, 0, w, h)
        if not self.pixbuf:
            raise IOError('Could not get pixbuf from active window')

        self.accessible_window = accessible_window
        self.texts = _extract_texts(accessible_window)


def _extract_texts(window):
    out = []

    def collect_chinese(accessible_object, _):
        text_object = get_text_object(accessible_object)
        if not text_object:
            return

        text = text_object.getText(0, -1)
        # NOTE: what if app is not using utf-8?
        debug('TEXT: %s' % text)
        if not may_contain_chinese(text):
            return

        out.append((text, text_object, accessible_object))

    visit_visible(window, collect_chinese)

    return out
