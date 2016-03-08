# coding=utf-8
import re

_CJK_TEXT_PATTERN = re.compile(ur'''
     [\u4e00-\u9fff]          # CJK Unified Ideographs
   | [\u3400-\u4dff]          # CJK Unified Ideographs Extension A
   | [\U00020000-\U0002a6df]  # CJK Unified Ideographs Extension B
   | [\uf900-\ufaff]          # CJK Compatibility Ideographs
   | [\U0002f800-\U0002fa1f]  # CJK Compatibility Ideographs Supplement
''', re.VERBOSE)


def may_contain_chinese(text):
    """
    :param text: a string
    :return: if False, the text definitely does not contain Chinese characters.  If True,
             the text might contain Chinese characters.
    """
    search = _CJK_TEXT_PATTERN.search(text)
    return search is not None
