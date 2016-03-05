# coding=utf-8
from __future__ import print_function

import gzip
import marisa_trie
import zhedod.dict


def _extract_keys(line, lineno):
    splits = line.split(' ', 2)
    if len(splits) != 3:
        raise ValueError("Line %d not in CEDICT format:\n%s" % (lineno, line))
    return splits[0:2]


def build(in_filename, in_file=None, logger=None):
    """
    Takes a dictionary file in CEDICT format and generates an index for use with zhedod.

    :param in_filename: Name of input CEDICT file
    :param in_file: IO object for dictionary file, if already opened.
    :param logger: Function accepting a string, used for logging.
    """
    if not in_file:
        with _open_for_read(in_filename) as f:
            return build(in_filename, in_file=f, logger=logger)

    if not logger:
        logger = print

    logger('Building from %s %s' % (in_filename, in_file))

    logger('Writing dict ...')
    with open(zhedod.dict.DICT_FILENAME, 'wb') as dict_out:
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
    marisa_trie.RecordTrie('<L', zip(trie_keys, trie_values)).save(zhedod.dict.INDEX_FILENAME)

    logger('Done!')


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