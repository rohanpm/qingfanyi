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
from qingfanyi.match import Match
from qingfanyi.navigator import Navigator

SAMPLE_GEOM = (100, 160, 200, 320)


class SignalSpy(object):
    def __init__(self, navigator):
        self.emits = []
        navigator.connect('current_match_changed', self.on_signal)

    def on_signal(self, sender, *args):
        self.emits.append(tuple([sender] + list(args)))


def test_empty_navigator():
    navigator = Navigator(SAMPLE_GEOM)
    assert navigator.current_match is None

    navigator.navigate_offset(-1)
    assert navigator.current_match is None

    navigator.navigate_offset(1)
    assert navigator.current_match is None


def test_navigate_offset_single():
    navigator = Navigator(SAMPLE_GEOM)
    spy = SignalSpy(navigator)
    match = Match('sample', [], [(0, 0, 10, 10)])
    navigator.add_matches([match])

    assert navigator.current_match is None
    assert spy.emits == []

    navigator.navigate_offset(-1)
    assert navigator.current_match is match
    assert spy.emits == [
        (navigator, None, match)
    ]

    navigator.navigate_offset(1)
    assert navigator.current_match is match
    assert len(spy.emits) == 1

    navigator.navigate_offset(57)
    assert navigator.current_match is match
    assert len(spy.emits) == 1


def test_add_match_retains_current():
    navigator = Navigator(SAMPLE_GEOM)
    spy = SignalSpy(navigator)

    # These matches are in the expected sorted order (by geometry),
    # but we will add them in a different order.
    matches = [
        Match('ab', [], [(0, 0, 20, 10)]),
        Match('a',  [], [(0, 0, 10, 10)]),
        Match('ab', [], [(10, 0, 20, 10)]),
        Match('a',  [], [(10, 0, 10, 10)]),
        Match('ab', [], [(40, 0, 10, 10)]),
        Match('ab', [], [(0, 30, 10, 10)]),
        Match('ab', [], [(0, 40, 10, 10)]),
    ]

    first_batch = [
        matches[0],
        matches[3],
        matches[5]
    ]
    second_batch = [
        matches[1],
        matches[2],
    ]
    third_batch = [
        matches[4],
        matches[6],
    ]

    navigator.add_matches(first_batch)
    assert navigator.current_match is None
    assert spy.emits == []

    # should navigate through in the expected order
    navigator.navigate_offset(1)
    assert navigator.current_match is first_batch[0]
    navigator.navigate_offset(1)
    assert navigator.current_match is first_batch[1]
    navigator.navigate_offset(1)
    assert navigator.current_match is first_batch[2]
    navigator.navigate_offset(1)
    assert navigator.current_match is first_batch[0]
    navigator.navigate_offset(1)
    assert navigator.current_match is first_batch[1]

    assert spy.emits == [
        (navigator, None,           first_batch[0]),
        (navigator, first_batch[0], first_batch[1]),
        (navigator, first_batch[1], first_batch[2]),
        (navigator, first_batch[2], first_batch[0]),
        (navigator, first_batch[0], first_batch[1]),
    ]
    spy.emits = []

    # now add some more
    navigator.add_matches(second_batch)

    # That should not have emitted anything or changed the current match
    assert spy.emits == []
    assert navigator.current_match is first_batch[1]

    navigator.navigate_offset(-1)
    assert navigator.current_match is matches[2]
    assert spy.emits == [
        (navigator, matches[3], matches[2])
    ]
    spy.emits = []

    # Add the last batch
    navigator.add_matches(third_batch)
    assert spy.emits == []
    assert navigator.current_match is matches[2]

    # It should have sorted all of these in the expected order
    assert navigator.matches == matches


def test_set_current_match_by_point():
    navigator = Navigator((100, 200, 500, 700))
    spy = SignalSpy(navigator)

    matches = [
        Match('ab', [], [(100, 200, 20, 10)]),
        Match('a',  [], [(100, 200, 10, 10)]),
        Match('ab', [], [(140, 200, 20, 10)]),
    ]

    navigator.add_matches(matches)

    # Overlapping matches - pick the longer one (by text)
    matched = navigator.set_current_match_by_point(5, 5)
    assert matched is matches[0]
    assert navigator.current_match is matched
    assert spy.emits == [
        (navigator, None, matched)
    ]
    spy.emits = []

    # Simple match
    matched = navigator.set_current_match_by_point(45, 5)
    assert matched is matches[2]
    assert navigator.current_match is matched
    assert spy.emits == [
        (navigator, matches[0], matched)
    ]
    spy.emits = []

    # Click the same match again, it should return it but not emit anything
    matched = navigator.set_current_match_by_point(46, 6)
    assert matched is matches[2]
    assert navigator.current_match is matched
    assert spy.emits == []

    # Click somewhere with no match, it should return None and not emit anything nor
    # change the current match.
    matched = navigator.set_current_match_by_point(200, -30)
    assert matched is None
    assert navigator.current_match is matches[2]
    assert spy.emits == []
