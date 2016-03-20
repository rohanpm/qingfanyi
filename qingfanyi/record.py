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

from qingfanyi import debug


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
        self.en_US_num = None
        self.pinyin_num = None

    @property
    def pinyin(self):
        out = [_pinyin_to_diacritic(w) for w in self.pinyin_num.split(' ')]
        return u' '.join(out)

    @property
    def en_US(self):
        """Processes numeric tones in the raw en_US texts."""
        return [_inner_pinyin_to_diacritic(w) for w in self.en_US_num]

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
        out.en_US_num = m.group(4).split('/')
        debug('type of en_US_num: %s' % type(out.en_US_num[0]))

        return out

_TONE_DIACRITIC = {
    1: u'\u0304',  # macron
    2: u'\u0301',  # acute accent
    3: u'\u030c',  # caron
    4: u'\u0300',  # grave accent
    5: '',         # neutral tone - nothing
}

def _pinyin_to_diacritic(word):
    # last character should be the tone
    try:
        tone = int(word[-1])
    except ValueError:
        # must be a special case...
        return word

    w = word[0:-1]

    w = w.replace('u:', u'ü')

    # https://en.wikipedia.org/wiki/Pinyin
    #
    # "the tone mark should always be placed by the order - a, o, e, i, u, ü, with the only exception being iu,
    # where the tone mark is placed on the u instead"
    chars = [u'iu']
    chars.extend([c for c in u'aoeiuü'])
    indexes = [(c, w.lower().find(c)) for c in chars]
    indexes = [(c, i) for (c, i) in indexes if i != -1]
    if not indexes:
        # Weird, a word without vowels?
        debug('vowel-less word? %s' % word)
        return word
    (c, index) = min(indexes, key=lambda (c, i): i)

    dia = _TONE_DIACRITIC[tone]
    offset = len(c)

    w = w[0:index+offset] + dia + w[index+offset:]

    return w


def _pinyins_to_diacritic(ws):
    out = u' '.join([_pinyin_to_diacritic(w) for w in ws.split()])
    debug('pinyins to diacritic %s returning %s' % (ws, out))
    return out


def _inner_pinyin_to_diacritic(text):
    # input example: u'CL:個|个[ge4],項|项[xiang4]'
    return re.sub(r'\[(([a-zA-Z]+\d ?)+)\]',
                  lambda m: u'[%s]' % _pinyins_to_diacritic(m.group(1)),
                  text)
