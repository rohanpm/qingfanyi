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
        ss = StateSet()
        ss.add(STATE_SHOWING)
        return ss


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
