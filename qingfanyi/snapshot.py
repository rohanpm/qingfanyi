# coding=utf-8
#import gtk

from gi.repository import Gdk

from qingfanyi import debug
from qingfanyi.atspi import get_text_object, visit_visible
from qingfanyi.text import may_contain_chinese


class Snapshot(object):
    def __init__(self, accessible_window, gdk_window, dic):
        self.matches = _process_chinese(accessible_window, dic)

        # getExtents returns some helper class.  I would rather unpack to a simple
        # tuple so it can be compared with rects from other contexts
        (x, y, w, h) = accessible_window.queryComponent().getExtents(0)
        self.rect = (x, y, w, h)

        frame = gdk_window.get_frame_extents()
        frame = (frame.x, frame.y, frame.width, frame.height)
        debug('acc window %s, gdk window %s' % (self.rect, frame))
        if self.rect != frame:
            raise ValueError(('AT-SPI and GDK reported different co-ordinates for '
                              'active window: %s vs %s' % (self.rect, frame)))

        (x, y, w, h) = gdk_window.get_geometry()
        self.geometry = (x, y, w, h)
        debug('taking snapshot of %s' % gdk_window)
        self.pixbuf = Gdk.pixbuf_get_from_window(gdk_window, 0, 0, w, h)
        if not self.pixbuf:
            raise IOError('Could not get pixbuf from active window')
        debug('snapshot is %s' % self.pixbuf)


def _extract_texts(window):
    out = []

    def collect_chinese(accessible_object, _):
        text_object = get_text_object(accessible_object)
        if not text_object:
            return

        text = text_object.getText(0, -1)
        # NOTE: what if app is not using utf-8?
        text = unicode(text, 'utf-8')
        if not may_contain_chinese(text):
            return

        out.append((text, text_object, accessible_object))

    visit_visible(window, collect_chinese)

    return out


def _process_chinese(window, dic):
    targets = _extract_texts(window)
    out = []

    for (text, text_object, accessible_object) in targets:
        matched = dic.parse_text(text)
        [m.init_rect(text_object) for m in matched]
        out.extend(matched)
        debug("found text: %s\n%s" % (text, matched))

    return out
