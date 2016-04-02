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
TEST_DICT = None


def get_dict_for_tests():
    from qingfanyi.dict import Dict
    from qingfanyi import index_builder

    global TEST_DICT
    if TEST_DICT is None:
        index_filename = 'tests/test.index'
        dict_filename = 'tests/test.dict'
        index_builder.ensure_index_built(index_filename, dict_filename)

        dic = Dict(dict_filename=dict_filename, index_filename=index_filename)
        dic.open()
        TEST_DICT = dic
    return TEST_DICT


def pytest_generate_tests(metafunc):
    if 'dic' in metafunc.fixturenames:
        metafunc.parametrize('dic',
                            [get_dict_for_tests()])