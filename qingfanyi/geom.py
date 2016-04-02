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


def rect_extend(rect1, rect2):
    (x1, y1, w1, h1) = rect1
    (x2, y2, w2, h2) = rect2

    x = min(x1, x2)
    y = min(y1, y2)
    w = max(x1 + w1, x2 + w2) - x
    h = max(y1 + h1, y2 + h2) - y
    return x, y, w, h


def any_rect_within(src_rect, rects):
    for rect in rects:
        if rect_within(src_rect, rect):
            return True


def rect_within(src_rect, rect):
    """Return True if rect is wholly contained within src_rect."""
    (src_x, src_y, src_w, src_h) = src_rect
    (x, y, w, h) = rect

    return x >= src_x and x+w <= src_x+src_w and y >= src_y and y+h <= src_y+src_h