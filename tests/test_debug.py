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
from contextlib import contextmanager

import qingfanyi


@contextmanager
def debug_enabled():
    oldval = qingfanyi._DEBUG
    try:
        qingfanyi._DEBUG = True
        yield
    finally:
        qingfanyi._DEBUG = oldval


def test_debug_can_output_bytes():
    with debug_enabled():
        qingfanyi.debug(b'test message: \x00\x01\xff\xfe')
    assert 'did not crash'


def test_debug_can_output_unicode():
    with debug_enabled():
        qingfanyi.debug(u'test message: 你好')
    assert 'did not crash'


def test_debug_can_invoke():
    with debug_enabled():
        qingfanyi.debug(lambda: 'test message: foo!')
    assert 'did not crash'
