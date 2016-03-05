# coding=utf-8
from contextlib import contextmanager
import marisa_trie

import mmap

from zhedod.record import Record

INDEX_FILENAME = 'zhedod.index'
DICT_FILENAME = 'zhedod.dict'


@contextmanager
def open_dict():
    out = Dict()
    out.open()
    try:
        yield out
    finally:
        out.close()


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
            out.append(Record.from_line(line))

        return out
