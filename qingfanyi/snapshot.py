# coding=utf-8
#import gtk

from gi.repository import Gdk
from pyatspi import Collection, StateSet

from qingfanyi import debug
from qingfanyi.atspi import get_text_object, visit_visible
from qingfanyi.text import may_contain_chinese


class Snapshot(object):
    def __init__(self, accessible_window, gdk_window, dic):
        (_, _, w, h) = gdk_window.get_geometry()
        (_, x, y) = gdk_window.get_origin()

        self.geometry = (x, y, w, h)
        debug('taking snapshot of %s' % gdk_window)
        self.pixbuf = Gdk.pixbuf_get_from_window(gdk_window, 0, 0, w, h)
        if not self.pixbuf:
            raise IOError('Could not get pixbuf from active window')

        self.all_matches = _process_chinese(accessible_window, dic)
        self.matches = [m
                        for m in self.all_matches
                        if _rect_within(self.geometry, m.rect)]

        debug('filtered %d matches to %d' % (len(self.all_matches), len(self.matches)))


def _extract_texts(window):
    out = []

    def collect_chinese(accessible_object, _):
        text_object = get_text_object(accessible_object)
        if not text_object:
            return

        text = text_object.getText(0, -1)
        # NOTE: what if app is not using utf-8?
        text = unicode(text, 'utf-8')
        debug('TEXT: %s' % text)
        if not may_contain_chinese(text):
            return

        out.append((text, text_object, accessible_object))

    visit_visible(window, collect_chinese)

    return out


def _process_chinese(window, dic):
    debug('BEGIN extracting texts from window...')
    targets = _extract_texts(window)
    debug('END extracting texts')
    out = []

    debug('BEGIN parsing texts')
    for (text, text_object, accessible_object) in targets:
        matched = dic.parse_text(text)
        [m.init_rect(text_object) for m in matched]
        out.extend(matched)
        debug("found text: %s\n%s" % (text, matched))
    debug('END parsing texts')

    return out


def _rect_within(src_rect, rect):
    (src_x, src_y, src_w, src_h) = src_rect
    (x, y, w, h) = rect

    return x >= src_x and x+w < src_x+src_w and y >= src_y and y+h < src_y+src_h
