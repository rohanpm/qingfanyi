# coding=utf-8


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