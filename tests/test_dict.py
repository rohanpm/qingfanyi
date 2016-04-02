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

from qingfanyi import dict


def test_close_closed_dict():
    dic = dict.Dict()
    with pytest.raises(RuntimeError):
        dic.close()


def test_open_opened_dict(dic):
    with pytest.raises(RuntimeError):
        dic.open()


def test_close_reopen(dic):
    dic.close()
    dic.open()
    assert dic[u'你好']