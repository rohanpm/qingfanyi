# coding=utf-8
from Queue import Queue

from gi.repository import Keybinder
from gi.repository import Gtk

from qingfanyi import debug


def run(queue):
    keystr = "<Ctrl><Alt>z"
    Keybinder.init()
    assert Keybinder.bind(keystr, _on_shortcut, queue)
    debug('keybinder active')
    Gtk.main()


def _on_shortcut(event, queue):
    debug('shortcut %s' % event)
    try:
        queue.put_nowait(event)
    except Queue.Full:
        # this means earlier shortcut is still being processed
        debug('  dropped shortcut')