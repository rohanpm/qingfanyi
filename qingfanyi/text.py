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
import re

_CJK_TEXT_PATTERN = re.compile(r'''
     [\u4e00-\u9fff]          # CJK Unified Ideographs
   | [\u3400-\u4dff]          # CJK Unified Ideographs Extension A
   | [\U00020000-\U0002a6df]  # CJK Unified Ideographs Extension B
   | [\uf900-\ufaff]          # CJK Compatibility Ideographs
   | [\U0002f800-\U0002fa1f]  # CJK Compatibility Ideographs Supplement
''', re.VERBOSE)


def may_contain_chinese(text):
    """
    :param text: a string
    :return: if False, the text definitely does not contain Chinese characters.  If True,
             the text might contain Chinese characters.
    """
    search = _CJK_TEXT_PATTERN.search(text)
    return search is not None
