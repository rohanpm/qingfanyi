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

from qingfanyi import text


@pytest.mark.parametrize('string,expected', [
    (u'hello, 世界', True),
    (u'hello, world', False),
    (u'hello, \U0001F30F', False),
    (u'multi-line\n课文', True),
])
def test_may_contain_chinese(string, expected):
    result = text.may_contain_chinese(string)
    assert result == expected
