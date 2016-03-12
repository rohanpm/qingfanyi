# coding=utf-8
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
        translate_pool.apply(_run_translate_process)

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