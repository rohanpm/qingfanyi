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

from qingfanyi.record import Record

_DATA_DIR = os.path.expanduser('~/.qingfanyi')

INDEX_FILENAME = os.path.join(_DATA_DIR, 'qingfanyi.index')
DICT_FILENAME = os.path.join(_DATA_DIR, 'qingfanyi.dict')


class Dict(object):
    def __init__(self, index_filename=INDEX_FILENAME, dict_filename=DICT_FILENAME):
        self._trie = None
        self._dict_file = None
        self._dict_mm = None
        self._opened = False
        self._index_filename = index_filename
        self._dict_filename = dict_filename

    def open(self):
        if self._opened:
            raise RuntimeError('Tried to open an open Dict!')

        self._trie = marisa_trie.RecordTrie('<L')
        self._trie.mmap(self._index_filename)
        self._dict_file = open(self._dict_filename)
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
