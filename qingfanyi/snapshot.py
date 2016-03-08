# coding=utf-8
import gtk

from qingfanyi import debug
from qingfanyi.atspi import get_text_object, visit_visible
from qingfanyi.text import may_contain_chinese


class Snapshot(object):
    def __init__(self, window, dic):
        self.matches = _process_chinese(window, dic)
        self.rect = window.queryComponent().getExtents(0)
        debug('snapshot window: %s' % self.rect)
        self.pixbuf = _pixbuf_from_screen(self.rect)


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


def _pixbuf_from_screen(rect):
    root = gtk.gdk.get_default_root_window()
    debug("root: %s" % root)
    debug("root extents: %s" % root.get_frame_extents())
    (x, y, w, h) = rect
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)
    pb = pb.get_from_drawable(root, root.get_colormap(), x, y, 0, 0, w, h)
    assert pb
    return pb
