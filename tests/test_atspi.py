# coding=utf-8
from pyatspi import STATE_SHOWING, StateSet

from qingfanyi import atspi


class FakeAccessibleObject(object):
    def __init__(self, ident=None, children=[]):
        self.ident = ident
        self._children = children

    def __getitem__(self, item):
        return self._children.__getitem__(item)

    def queryText(self):
        raise NotImplementedError


class VisibleObject(FakeAccessibleObject):
    def getState(self):
        return StateSet(STATE_SHOWING)


class InvisibleObject(FakeAccessibleObject):
    def getState(self):
        return StateSet()


def test_visit_visible():
    called = []

    def callback(object, level):
        called.append((object.ident, level))

    root = VisibleObject('root', [
        InvisibleObject('invis1', [
            VisibleObject('vis-under-invis')
        ]),
        VisibleObject('vis1', [
            VisibleObject('vis2_1'),
            VisibleObject('vis2_2'),
            InvisibleObject('invis-under-vis')
        ])
    ])

    atspi.visit_visible(root, callback)

    assert called == [
        ('root', 0),
        ('vis1', 1),
        ('vis2_1', 2),
        ('vis2_2', 2),
    ]


def test_get_text_nontext_object():
    got = atspi.get_text_object(FakeAccessibleObject())
    assert got is None


def test_get_text_text_object():
    sentinel = object()

    class TextObject(object):
        def queryText(self):
            return sentinel

    got = atspi.get_text_object(TextObject())
    assert got is sentinel
