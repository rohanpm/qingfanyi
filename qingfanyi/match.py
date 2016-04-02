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
from qingfanyi import debug
from qingfanyi.geom import rect_extend


class Match(object):
    def __init__(self, offset, text, records, rect=None):
        self.offset = offset
        self.text = text
        self.records = records
        self.rects = []

    def init_rects(self, text_object):
        """
        Initialize the rects attribute via AT-SPI queries.

        This assembles the minimum amount of rects to cover the matched text without
        returning any rect covering multiple lines (e.g. in case the matched text was
        word-wrapped).

        :param text_object: an accessible object's text interface
        """
        i = self.offset
        end = self.offset + len(self.text)
        out = []
        current_rect = None

        while i < end:
            this_rect = text_object.getCharacterExtents(i, 0)
            debug('index %d rect %s' % (i, this_rect))
            if current_rect:
                # Can we extend the current_rect to cover this_rect without increasing
                # its height?
                (curr_x, curr_y, curr_w, curr_h) = current_rect
                (this_x, this_y, this_w, this_h) = this_rect

                if curr_y == this_y and curr_h == this_h:
                    # Yes. Keep extending current rect.
                    debug('  extending')
                    current_rect = rect_extend(current_rect, this_rect)
                else:
                    # No. Save current rect and start a new one.
                    debug('  new rect')
                    out.append(current_rect)
                    current_rect = this_rect
            else:
                current_rect = this_rect
            i += 1

        debug('  end')
        out.append(current_rect)

        self.rects = out

    def __repr__(self):
        return 'Match%s' % self.__dict__.__repr__()


