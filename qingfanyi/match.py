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


class Match(object):
    def __init__(self, offset, text, records, rect=None):
        self.offset = offset
        self.text = text
        self.records = records
        self.rect = None

    def init_rect(self, text_object):
        """
        Initialize the rect attribute via AT-SPI queries.

        :param text_object: an accessible object's text interface
        """
        end = self.offset + len(self.text)
        self.rect = text_object.getRangeExtents(self.offset, end, 0)

    def __repr__(self):
        return 'Match%s' % self.__dict__.__repr__()