# coding=utf-8
from contextlib import contextmanager

import qingfanyi


@contextmanager
def debug_enabled():
    oldval = qingfanyi._DEBUG
    try:
        qingfanyi._DEBUG = True
        yield
    finally:
        qingfanyi._DEBUG = oldval


def test_debug_can_output_bytes():
    with debug_enabled():
        qingfanyi.debug(b'test message: \x00\x01\xff\xfe')
    assert 'did not crash'


def test_debug_can_output_unicode():
    with debug_enabled():
        qingfanyi.debug(u'test message: 你好')
    assert 'did not crash'


def test_debug_can_invoke():
    with debug_enabled():
        qingfanyi.debug(lambda: 'test message: foo!')
    assert 'did not crash'
