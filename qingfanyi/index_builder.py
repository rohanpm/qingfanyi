# coding=utf-8
import gzip
import marisa_trie
import qingfanyi.dict
import os


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


