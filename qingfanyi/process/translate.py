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
import threading
import traceback

from gi.repository import GLib
from gi.repository import Gtk
from pyatspi import Registry

import qingfanyi.styles
from qingfanyi import debug
from qingfanyi.dict import Dict
from qingfanyi.popup_manager import PopupManager
from qingfanyi.snapshot import Snapshot
from qingfanyi.snapshot_matcher import SnapshotMatcher
from qingfanyi.translate_window import TranslateWindow
from qingfanyi.wm import active_window


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

        qingfanyi.styles.init()

        debug('taking snapshot')
        snapshot = Snapshot(accessible_window, gdk_window)

        debug('creating translate window')
        translate_win = TranslateWindow(snapshot)
        translate_win.show()

        snapshot_matcher = SnapshotMatcher(snapshot, self.dic)
        snapshot_matcher.connect('match-found', translate_win.add_match)
        snapshot_matcher.start()

        PopupManager(translate_win)

        # nested loop to make run() blocking
        translate_win.connect('hide', lambda *_: Gtk.main_quit())
        Gtk.main()

    def run_event_loop(self):
        debug('starting at-spi loop')
        Registry.start(gil=False)

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
