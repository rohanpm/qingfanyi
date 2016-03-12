# coding=utf-8
import time
from pyatspi import Registry

from qingfanyi import debug
from qingfanyi.atspi import active_window
from qingfanyi.dict import Dict
from qingfanyi.snapshot import Snapshot
from qingfanyi.translate_window import TranslateWindow

from gi.repository import Gtk
from gi.repository import GLib

import threading
import traceback


class Translate(object):

    def __init__(self):
        self.dic = Dict()
        self.dic.open()
        self.condvar = threading.Condition()
        self.error = None


    def run_in_other_thread(self):
        self.condvar.acquire()
        GLib.idle_add(self.run_in_this_thread)
        self.condvar.wait()
        debug('run in other thread done')
        if self.error:
            raise self.error

    def run_in_this_thread(self):
        self.condvar.acquire()
        self.error = None
        try:
            self.run()
        except StandardError as e:
            traceback.print_exc()
            self.error = e
        finally:
            self.condvar.notify()
            self.condvar.release()

    def run(self):
        debug('translate running...')
        (accessible_window, gdk_window) = active_window()
        if not accessible_window:
            debug('No active window.  Do nothing.')
            return

        debug('active: %s' % accessible_window)

        debug('taking snapshot')
        snapshot = Snapshot(accessible_window, gdk_window, self.dic)

        debug('creating translate window')
        translate_win = TranslateWindow(snapshot)
        translate_win.show()

        # nested loop to make run() blocking
        translate_win.connect('hide', lambda *_: Gtk.main_quit())
        Gtk.main()

    def run_event_loop(self):
        Registry.start(gil=True)

    def __del__(self):
        debug('closing.')
        self.dic.close()
        self.dic = None

_INSTANCE = None


def run():
    if not _INSTANCE:
        raise ValueError('run() called before init()')
    _INSTANCE.run_in_other_thread()
    debug('run complete')


def init():
    global _INSTANCE
    if _INSTANCE:
        raise ValueError('init() called more than once')

    _INSTANCE = Translate()

    thread = threading.Thread(target=_INSTANCE.run_event_loop)
    thread.start()
