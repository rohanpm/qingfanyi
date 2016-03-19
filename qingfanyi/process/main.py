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
from multiprocessing import Queue, Process, Pool

from qingfanyi import debug

import signal
import os


def run():
    activate_queue = Queue(1)
    keybind_process = Process(target=_start_keybind_process, args=(activate_queue,))
    keybind_process.start()

    translate_pool = Pool(processes=1, initializer=_init_translate_process,
                          maxtasksperchild=1)

    stop = []
    def stop_now(*_):
        stop.append(None)
        activate_queue.close()
        debug('stop due to signal')
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    signal.signal(signal.SIGTERM, stop_now)
    signal.signal(signal.SIGINT, stop_now)

    while not stop:
        got = None
        try:
            got = activate_queue.get()
        except:
            if not stop:
                raise
        debug('parent got: %s' % got)

        if not got:
            break

        debug('invoke translate')
        try:
            translate_pool.apply(_run_translate_process)
        except StandardError as e:
            debug('failed: %s' % e)

    debug('exiting normally')
    keybind_process.terminate()

    # FIXME: this always hangs.  Why?
    # That's why we use _exit instead.
    #translate_pool.terminate()

    os._exit(0)


def _start_keybind_process(queue):
    debug('keybind process starting')
    import qingfanyi.process.keybind
    qingfanyi.process.keybind.run(queue)


def _init_translate_process(*args):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    debug('would init translate process %s' % (args,))
    import qingfanyi.process.translate
    qingfanyi.process.translate.init()


def _run_translate_process(*args):
    debug('would run translate process %s' % (args,))
    import qingfanyi.process.translate
    qingfanyi.process.translate.run()