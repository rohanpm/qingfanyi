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
import marisa_trie
import mmap

import os.path

from qingfanyi.match import Match
from qingfanyi.record import Record
from qingfanyi.text import may_contain_chinese

_DATA_DIR = os.path.expanduser('~/.qingfanyi')

INDEX_FILENAME = os.path.join(_DATA_DIR, 'qingfanyi.index')
DICT_FILENAME = os.path.join(_DATA_DIR, 'qingfanyi.dict')


class Dict(object):
    def __init__(self):
        self._trie = None
        self._dict_file = None
        self._dict_mm = None
        self._opened = False

    def open(self):
        if self._opened:
            raise RuntimeError('Tried to open an open Dict!')

        self._trie = marisa_trie.RecordTrie('<L')
        self._trie.mmap(INDEX_FILENAME)
        self._dict_file = open(DICT_FILENAME)
        self._dict_mm = mmap.mmap(self._dict_file.fileno(), 0, access=mmap.ACCESS_READ)
        self._opened = True

    def close(self):
        if not self._opened:
            raise RuntimeError('Tried to close a closed Dict!')

        self._dict_mm.close()
        self._dict_file.close()
        self._trie = self._dict_file = self._dict_mm = self._opened = None

    def prefixes(self, text):
        return self._trie.prefixes(text)

    def __getitem__(self, item):
        match = self._trie[item]
        out = []
        for m in match:
            (index,) = m

            # This is the index into dict_mm.
            # Read that line.
            end_index = self._dict_mm.find('\n', index)
            line = self._dict_mm[index:end_index]
            line = unicode(line, 'utf-8')
            out.append(Record.from_line(line))

        return out

    def parse_text(self, text):
        """
        Parses a string and returns all records looked up from the dictionary.
        The returned value is a list of Match objects.
        """
        out = []
        offset = 0
        while text:
            advance = 1

            # Explicitly skip non-CJK texts.
            #
            # The reason is that there are some entries in the dictionary for short
            # slang terms written using common English letters or symbols, e.g. "A".
            # Since this program is expected to work with mixed English and Chinese text,
            # these would most likely be false positives.
            if may_contain_chinese(text[0]):
                prefs = self.prefixes(text)

                # Get the longest match
                prefs = sorted(prefs, key=len, reverse=True)

                if prefs:
                    pref = prefs[0]
                    records = self[pref]
                    out.append(Match(offset, pref, records))
                    advance = len(pref)

            offset += advance
            text = text[advance:]

        return out

