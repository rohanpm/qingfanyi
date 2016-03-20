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
from pyatspi import Collection, StateSet

from qingfanyi import debug
from qingfanyi.atspi import get_text_object, visit_visible
from qingfanyi.text import may_contain_chinese


class Snapshot(object):
    def __init__(self, accessible_window, gdk_window, dic):
        (_, _, w, h) = gdk_window.get_geometry()
        (_, x, y) = gdk_window.get_origin()

        self.geometry = (x, y, w, h)
        debug('taking snapshot of %s' % gdk_window)
        self.pixbuf = Gdk.pixbuf_get_from_window(gdk_window, 0, 0, w, h)
        if not self.pixbuf:
            raise IOError('Could not get pixbuf from active window')

        self.accessible_window = accessible_window
        self.dic = dic
        self._matches = None


    @property
    def matches(self):
        if self._matches is None:
            all_matches = _process_chinese(self.accessible_window, self.dic)
            filtered_matches = [m
                                for m in all_matches
                                if _any_rect_within(self.geometry, m.rects)]
            debug('filtered %d matches to %d' % (len(all_matches), len(filtered_matches)))

            debug('sorting matches by rect...')
            sorted_matches = sorted(filtered_matches, key=_match_sort_key)
            debug('...done sorting')
            self._matches = sorted_matches
        return self._matches


def _extract_texts(window):
    out = []

    def collect_chinese(accessible_object, _):
        text_object = get_text_object(accessible_object)
        if not text_object:
            return

        text = text_object.getText(0, -1)
        # NOTE: what if app is not using utf-8?
        text = unicode(text, 'utf-8')
        debug('TEXT: %s' % text)
        if not may_contain_chinese(text):
            return

        out.append((text, text_object, accessible_object))

    visit_visible(window, collect_chinese)

    return out


def _process_chinese(window, dic):
    debug('BEGIN extracting texts from window...')
    targets = _extract_texts(window)
    debug('END extracting texts')
    out = []

    debug('BEGIN parsing texts')
    for (text, text_object, accessible_object) in targets:
        matched = dic.parse_text(text)
        [m.init_rects(text_object) for m in matched]
        out.extend(matched)
        debug("found text: %s\n%s" % (text, matched))
    debug('END parsing texts')

    return out


def _any_rect_within(src_rect, rects):
    for rect in rects:
        if _rect_within(src_rect, rect):
            return True


def _rect_within(src_rect, rect):
    (src_x, src_y, src_w, src_h) = src_rect
    (x, y, w, h) = rect

    return x >= src_x and x+w < src_x+src_w and y >= src_y and y+h < src_y+src_h


def _match_sort_key(match):
    (x, y, w, h) = match.rects[0]
    return y, x
