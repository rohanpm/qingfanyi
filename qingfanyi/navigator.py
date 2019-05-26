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


class Navigator(GObject.Object):
    """Holds a sequence of matches and manages navigation through them."""
    __gsignals__ = {
        # current selected match changed from (old) to (new)
        'current_match_changed': (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE,
                                  (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT))
    }

    def __init__(self, geometry):
        GObject.Object.__init__(self)
        self.current_match_index = None
        self.matches = []
        self.geometry = geometry

    @property
    def current_match(self):
        if self.current_match_index is None:
            return None
        return self.matches[self.current_match_index]

    def add_matches(self, matches):
        debug('BEGIN add %d matches' % len(matches))

        # Retain the current match if there is one.
        current = self.current_match

        self.matches.extend(matches)
        self.matches.sort(key=_match_sort_key)

        if current:
            # Update current_match_index to new correct value.
            # It could be anywhere from its previous value up to +len(matches).
            for i in range(self.current_match_index,
                           self.current_match_index + len(matches) + 1):
                if self.matches[i] is current:
                    self.current_match_index = i
                    break

        debug('END add matches')

        pass

    def set_current_match(self, idx, match):
        # TODO: clean up params (idx and match not both required...)
        if self.current_match_index == idx:
            return

        prev_match = self.current_match
        self.current_match_index = idx

        self.emit('current_match_changed', prev_match, self.current_match)

    def set_current_match_by_point(self, x, y):
        match = _find_match(self.matches, self.geometry, x, y)
        if match and match is not self.current_match:
            # TODO clean up args
            self.set_current_match(self.matches.index(match), match)
        return match

    def navigate_offset(self, offset):
        if not self.matches:
            return

        idx = prev_idx = self.current_match_index
        if idx is None:
            if offset == 1:
                idx = 0
            else:
                idx = -1
        else:
            idx += offset

        size = len(self.matches)
        while idx >= size:
            idx -= size
        while idx < 0:
            idx += size

        debug('navigate from %s by %s gives %s' % (prev_idx, offset, idx))

        self.set_current_match(idx, self.matches[idx])



def _match_sort_key(match):
    (x, y, w, h) = match.rects[0]
    return y, x, -len(match.text)


def _find_match(matches, geometry, event_x, event_y):
    (window_x, window_y, _, _) = geometry

    # There can be multiple matches, e.g. if user clicked on 你 from 你好, then
    # there will be a match for both 你 and 你好.
    # Currently we will always favor the leftmost and longest match.
    # We don't explicitly need code to do that, because they're already sorted that
    # way.

    for m in matches:
        for (x, y, w, h) in m.rects:
            x -= window_x
            y -= window_y
            if x <= event_x < x + w and y <= event_y < y + h:
                return m
