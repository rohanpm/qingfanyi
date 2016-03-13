# coding=utf-8
from gi.repository import GObject

from qingfanyi import debug
from qingfanyi.popup_window import PopupWindow


class PopupManager(GObject.GObject):
    """
    Manager class connecting translation window with popups.

    Current design allows only one popup at a time.
    """

    def __init__(self, translation_window):
        translation_window.connect('lookup-requested', self.popup_for_match)
        self.active = None

    def popup_for_match(self, sender, match):
        debug('would popup for %s' % match)
        if self.active:
            self.active.destroy()
        self.active = self.make_active(sender, match)

    def unset_active(self):
        debug('unset active')
        self.active = None

    def make_active(self, sender, match):
        win = PopupWindow(sender, match)
        win.connect('hide', lambda *_: self.unset_active())
        win.show()
        return win
