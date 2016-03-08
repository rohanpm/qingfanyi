# coding=utf-8
from contextlib import contextmanager
import marisa_trie

import mmap
import os.path

from qingfanyi.match import Match
from qingfanyi.record import Record

_DATA_DIR = os.path.expanduser('~/.qingfanyi')

INDEX_FILENAME = os.path.join(_DATA_DIR, 'qingfanyi.index')
DICT_FILENAME = os.path.join(_DATA_DIR, 'qingfanyi.dict')

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

    def parse_text(self, text):
        """
        Parses a string and returns all records looked up from the dictionary.
        The returned value is a list of Match objects.
        """
        out = []
        offset = 0
        while text:
            prefs = self.prefixes(text)

            # Get the longest match
            prefs = sorted(prefs, key=len, reverse=True)

            advance = 1

            if prefs:
                pref = prefs[0]
                records = self[pref]
                out.append(Match(offset, pref, records))
                advance = len(pref)

            offset += advance
            text = text[advance:]

        return out

