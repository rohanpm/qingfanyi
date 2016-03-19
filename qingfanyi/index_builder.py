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
from __future__ import print_function
import gzip
import marisa_trie
import os
from pkg_resources import resource_stream

import qingfanyi.dict
from qingfanyi import debug


def _extract_keys(line, lineno):
    splits = line.split(' ', 2)
    if len(splits) != 3:
        raise ValueError("Line %d not in CEDICT format:\n%s" % (lineno, line))
    return splits[0:2]


def _ensure_index_dir():
    index_path = qingfanyi.dict.INDEX_FILENAME
    path = os.path.dirname(index_path)
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def _open_for_read(filename):
    """
    Tries to open a file which may or may not be gzip-compressed.
    """
    try:
        out = gzip.open(filename)
        # open does not try to read any data yet, so to force failure now,
        # try to seek a bit.
        out.seek(1)
        out.seek(0)
        return out
    except IOError:
        # maybe it wasn't gzip...
        return open(filename)


def build(in_filename, in_file=None, logger=None):
    """
    Takes a dictionary file in CEDICT format and generates an index for use with
    qingfanyi.

    :param in_filename: Name of input CEDICT file
    :param in_file: IO object for dictionary file, if already opened.
    :param logger: Function accepting a string, used for logging.
    """
    if not in_file:
        with _open_for_read(in_filename) as f:
            return build(in_filename, in_file=f, logger=logger)

    if not logger:
        logger = qingfanyi.debug

    logger('Building from %s' % in_filename)

    logger('Writing dict ...')
    _ensure_index_dir()
    with open(qingfanyi.dict.DICT_FILENAME, 'wb') as dict_out:
        index = 0
        trie_keys = []
        trie_values = []
        lineno = 0
        for line in in_file:
            lineno += 1
            if line.startswith('#'):
                continue
            if not line.strip():
                continue
            keys = _extract_keys(line, lineno)
            for key in keys:
                key = unicode(key, 'utf-8')
                trie_keys.append(key)
                trie_values.append((index,))
            dict_out.write(line)
            index += len(line)

    logger('Writing index ...')
    marisa_trie.RecordTrie('<L', zip(trie_keys, trie_values)).save(
        qingfanyi.dict.INDEX_FILENAME)

    logger('Done!')


def ensure_index_built():
    if os.path.exists(qingfanyi.dict.INDEX_FILENAME):
        debug('Index is already built.')
        return

    print('Building index on first use.')

    resource_name = 'data/cedict_1_0_ts_utf-8_mdbg.txt'
    stream = resource_stream('qingfanyi', resource_name)
    assert stream
    build(resource_name, stream, logger=print)