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

import signal
import os

from qingfanyi import debug
from qingfanyi.index_builder import ensure_index_built


def run():
    ensure_index_built()

    activate_queue = Queue(1)
    keybind_process = Process(target=_start_keybind_process, args=(activate_queue,))
    keybind_process.start()

    translate_pool = Pool(processes=1, initializer=_init_translate_process,
                          maxtasksperchild=1)

    stop = []

    def stop_now(sig, *_):
        stop.append(sig)
        activate_queue.close()
        debug('stop due to signal %s' % sig)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGUSR1, signal.SIG_DFL)

    signal.signal(signal.SIGTERM, stop_now)
    signal.signal(signal.SIGINT, stop_now)
    signal.signal(signal.SIGUSR1, stop_now)

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

    if stop[0] == signal.SIGUSR1:
        # keybind child signaled an error
        keybind_process.join(10)
        os._exit(7)

    debug('exiting normally')
    keybind_process.terminate()

    # FIXME: this always hangs.  Why?
    # That's why we use _exit instead.
    #translate_pool.terminate()

    os._exit(0)


def _start_keybind_process(queue):
    debug('keybind process starting')
    import qingfanyi.process.keybind
    try:
        qingfanyi.process.keybind.run(queue)
    except:
        os.kill(os.getppid(), signal.SIGUSR1)
        raise


def _init_translate_process(*args):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    debug('init translate process %s' % (args,))
    import qingfanyi.process.translate
    qingfanyi.process.translate.init()


def _run_translate_process(*args):
    debug('run translate process %s' % (args,))
    import qingfanyi.process.translate
    qingfanyi.process.translate.run()