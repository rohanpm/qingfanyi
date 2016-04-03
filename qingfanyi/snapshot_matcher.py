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
from gi.repository import GObject, GLib

import time

from qingfanyi import debug
from qingfanyi.geom import join_rects
from qingfanyi.match import Match
from qingfanyi.text import may_contain_chinese

BATCH_TIME = 0.2


class SnapshotMatcher(GObject.Object):
    """This class asynchronously extracts ``Match`` objects from a ``Snapshot``."""
    __gsignals__ = {
        'matches-found': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                          (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, snapshot, dic):
        GObject.Object.__init__(self)
        self._dic = dic
        self._snapshot = snapshot
        self._texts = reversed(snapshot.texts)
        self._cursor = None
        self._stop = False

    def start(self):
        """Start extracting matches.

        After this method is called, the ``match-found`` signal will be emitted
        asynchronously as Chinese text is parsed from the snapshot.
        """
        GLib.idle_add(self._match_next)
        self._stop = False

    def stop(self):
        self._stop = True

    def _match_next(self):
        if self._stop:
            return False

        matches = []
        out = True

        begin = time.time()

        def should_stop():
            return time.time() - begin > BATCH_TIME

        while True:
            try:
                if self._cursor is None:
                    self._cursor = Cursor(*self._texts.next())
                self._cursor = self._cursor_next(self._cursor, matches)
            except StopIteration:
                debug('no more text to match')
                out = False
                break
            if should_stop():
                break

        self.emit('matches-found', matches)

        return out

    def _cursor_next(self, cursor, matches):
        cursor.step()
        text = cursor.current_text
        debug('cursor idx %d, match text: %s' % (cursor.index,
                                                 text))
        if cursor.finished:
            return

        prefixes = self._dic.prefixes(text)
        for pref in prefixes:
            debug('prefix: %s' % pref)
            records = self._dic[pref]
            rects = cursor.current_rects(len(pref))
            rects = join_rects(rects)
            matches.append(Match(pref, records, rects))

        return cursor


class Cursor(object):
    def __init__(self, text, text_object, accessible_object):
        self.text = text
        self.text_object = text_object
        self.accessible_object = accessible_object
        self.index = len(text)
        self.rects = {}

    def step(self):
        self.index -= 1
        while not may_contain_chinese(self.current_text[0]) and not self.finished:
            self.index -= 1
        if self.finished:
            return

        extents = self.text_object.getCharacterExtents(self.index, 0)
        debug('get rect for index %d == %s' % (self.index, extents))
        self.rects[self.index] = extents

    @property
    def finished(self):
        return self.index < 0

    @property
    def current_text(self):
        return self.text[self.index:]

    def current_rects(self, length):
        out = []
        i = 0
        rect_index = self.index + i
        while rect_index in self.rects and i < length:
            out.append(self.rects[rect_index])
            i += 1
            rect_index += 1
        return out
