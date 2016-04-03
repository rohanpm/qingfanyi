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


def rect_extend(rect1, rect2):
    (x1, y1, w1, h1) = rect1
    (x2, y2, w2, h2) = rect2

    x = min(x1, x2)
    y = min(y1, y2)
    w = max(x1 + w1, x2 + w2) - x
    h = max(y1 + h1, y2 + h2) - y
    return x, y, w, h


def rect_within(src_rect, rect):
    """Return True if rect is wholly contained within src_rect."""
    (src_x, src_y, src_w, src_h) = src_rect
    (x, y, w, h) = rect

    return x >= src_x and x+w <= src_x+src_w and y >= src_y and y+h <= src_y+src_h


def join_rects(rects):
    """
    Given a list of rects for character extents, which must be ordered left-to-right
    and top-to-bottom, attempts to return a smaller list of larger rects covering the
    same area.

    Rects will be joined left-to-right, but not top-to-bottom, i.e. rects will not be
    extended over a line break.

    For example, if given rects for text like this:

       你好吗

    ... the 3 rects for each character will be joined to 1, but if given rects for
    text like this:

       你好
       吗

    ... the 3 rects for each character will be joined to 1 for the first line and 1
    for the second line, returning 2 rects total, neither spanning the line break.
    """
    i = 0
    end = len(rects)
    out = []
    current_rect = None

    while i < end:
        this_rect = rects[i]
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

    return out