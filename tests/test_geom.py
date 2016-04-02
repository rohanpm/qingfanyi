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
import pytest

from qingfanyi import geom


@pytest.mark.parametrize('rect1,rect2,expected_rect', [
    ((0, 0, 1, 1), (0, 0, 2, 2), (0, 0, 2, 2)),
    ((0, 0, 1, 2), (0, 0, 2, 1), (0, 0, 2, 2)),
    ((0, 0, 1, 3), (0, 0, 2, 1), (0, 0, 2, 3)),
    ((-50, -30, 100, 80), (400, 600, 1, 1), (-50, -30, 451, 631)),
])
def test_rect_extend(rect1, rect2, expected_rect):
    got = geom.rect_extend(rect1, rect2)
    assert got == expected_rect


@pytest.mark.parametrize('src_rect,rect,expected', [
    ((0, 0, 100, 100), (0, 0, 100, 100), True),
    ((0, 0, 100, 100), (25, 25, 50, 50), True),
    ((0, 0, 100, 100), (0, 0, 100, 101), False),
    ((0, 0, 100, 100), (0, 0, 101, 100), False),
    ((0, 0, 100, 100), (0, -1, 100, 100), False),
    ((0, 0, 100, 100), (-1, 0, 100, 100), False),
    ((-50, -30, 20, 10), (-40, -25, 10, 5), True),
])
def test_rect_within(src_rect, rect, expected):
    got = geom.rect_within(src_rect, rect)
    assert got == expected
