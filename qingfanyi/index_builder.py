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

import marisa

import os
import json
from pkg_resources import resource_stream

import qingfanyi.dict
from qingfanyi import debug


def _extract_keys(line, lineno):
    splits = line.split(b' ', 2)
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


def build(in_filename, in_file, logger=None,
          out_index_filename=qingfanyi.dict.INDEX_FILENAME,
          out_dict_filename=qingfanyi.dict.DICT_FILENAME):
    """
    Takes a dictionary file in CEDICT format and generates an index for use with
    qingfanyi.

    :param in_filename: Name of input CEDICT file
    :param in_file: IO object for dictionary file
    :param logger: Function accepting a string, used for logging.
    """

    if not logger:
        logger = qingfanyi.debug

    logger('Building from %s' % in_filename)

    logger('Writing dict ...')
    _ensure_index_dir()

    ks = marisa.Keyset()

    with open(out_dict_filename, 'wb') as dict_out:
        index = 0
        # trie_keys = []
        num_keys = 0
        trie_values = {}
        lineno = 0
        for line in in_file:
            lineno += 1
            if line.startswith(b'#'):
                continue
            if not line.strip():
                continue
            keys = _extract_keys(line, lineno)
            for key_bytes in keys:
                key_str = str(key_bytes, 'utf-8')
                ks.push_back(key_str)

                # trie_keys.append(key_str)
                trie_values.setdefault(key_str, []).append(index)
            dict_out.write(line)
            index += len(line)

    logger('Writing index ...')
    trie = marisa.Trie()
    trie.build(ks)

    trie.save(out_index_filename)

    key_id_to_index = [0]*ks.num_keys()
    for i in range(0, ks.num_keys()):
        key_id = ks.key_id(i)
        key_str = ks.key_str(i)
        key_id_to_index[key_id] = list(set(trie_values[key_str]))

    with open(out_index_filename, mode='a') as f:
        json.dump(key_id_to_index, f, separators=(',', ':'))

    logger('Done!')


def ensure_index_built(index_filename=qingfanyi.dict.INDEX_FILENAME,
                       dict_filename=qingfanyi.dict.DICT_FILENAME):
    if os.path.exists(index_filename):
        debug('Index is already built.')
        return

    print('Building index on first use.')

    resource_name = 'data/cedict_1_0_ts_utf-8_mdbg.txt'
    stream = resource_stream('qingfanyi', resource_name)
    assert stream
    build(resource_name, stream, logger=print,
          out_dict_filename=dict_filename,
          out_index_filename=index_filename)