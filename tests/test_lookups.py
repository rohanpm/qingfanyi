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


def test_lookup(dic):
    lookup = dic[u'汉堡']

    assert len(lookup) == 2

    hamburg = lookup[0]
    hamburger = lookup[1]

    assert hamburg.en_US == [u'Hamburg (German city)']
    assert hamburg.pinyin_num == u'Han4 bao3'
    assert hamburg.pinyin == u'Ha\u0300n ba\u030co'
    assert hamburg.zh_CN == u'汉堡'
    assert hamburg.zh_TW == u'漢堡'

    assert hamburger.en_US == [u'hamburger (loanword)']
    assert hamburger.pinyin_num == u'han4 bao3'
    assert hamburger.pinyin == u'ha\u0300n ba\u030co'
    assert hamburger.zh_TW == hamburg.zh_TW
    assert hamburger.zh_CN == hamburg.zh_CN


def test_inner_diacritic(dic):
    # 不材 不材 [bu4 cai2] /untalented/I/me (humble)/also written 不才[bu4 cai2]/
    lookup = dic[u'不材']

    assert len(lookup) == 1

    english = lookup[0].en_US[-1]
    assert english == u'also written 不才[bu\u0300 ca\u0301i]'