# coding=utf-8
import re


class Record(object):
    _CEDICT_PATTERN = re.compile(
        r"""
            ([^ ]+)        # traditional
            \s
            ([^ ]+)        # simplified
            \s
            \[ ([^\]]+) \] # pinyin
            \s
            /
            (.+)           # English
            /
            \s*
            \Z
        """, re.VERBOSE)

    def __init__(self):
        self.zh_CN = None
        self.zh_TW = None
        self.en_US = None
        self.pinyin_num = None

    @property
    def pinyin(self):
        out = [_pinyin_to_diacritic(w) for w in self.pinyin_num.split(' ')]
        return u' '.join(out)

    def __str__(self):
        return "%s [%s]:\n  %s" % (self.zh_CN,
                                   self.pinyin.encode('utf-8'),
                                   "\n  ".join(self.en_US))

    def __repr__(self):
        return 'Record%s' % self.__dict__.__repr__()

    @staticmethod
    def from_line(line):
        out = Record()
        m = Record._CEDICT_PATTERN.match(line)

        if not m:
            raise ValueError("Not a valid CEDICT-formatted record: %s" % line)

        out.zh_TW = m.group(1)
        out.zh_CN = m.group(2)
        out.pinyin_num = m.group(3)
        out.en_US = m.group(4).split('/')

        return out

_TONE_DIACRITIC = {
    1: u'\u0304',  # macron
    2: u'\u0301',  # acute accent
    3: u'\u030c',  # caron
    4: u'\u0300',  # grave accent
    5: '',         # neutral tone - nothing
}

def _pinyin_to_diacritic(w):
    # last character should be the tone
    try:
        tone = int(w[-1])
    except ValueError:
        # must be a special case...
        return w

    w = w[0:-1]

    w = unicode(w, 'utf-8')

    w = w.replace('u:', u'ü')

    # https://en.wikipedia.org/wiki/Pinyin
    #
    # "the tone mark should always be placed by the order - a, o, e, i, u, ü, with the only exception being iu,
    # where the tone mark is placed on the u instead"
    chars = [u'iu']
    chars.extend([c for c in u'aoeiuü'])
    indexes = [(c, w.find(c)) for c in chars]
    indexes = [(c, i) for (c, i) in indexes if i != -1]
    (c, index) = min(indexes, key=lambda (c, i): i)

    dia = _TONE_DIACRITIC[tone]
    offset = len(c)

    w = w[0:index+offset] + dia + w[index+offset:]

    return w

