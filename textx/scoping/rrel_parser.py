from arpeggio import Optional, ZeroOrMore, EOF
from arpeggio import RegExMatch as _


def id():
    return _(r'[^\d\W]\w*\b')  # from lang.py


def parent():
    return 'parent', '(', id, ')'


def navigation():
    return Optional('~'), id


def brackets():
    return '(', path, ')'


def dots():
    return _(r'\.+')


def path_element():
    return [parent, brackets, navigation]


def zero_or_more():
    return path_element, '*'


def path():
    return Optional(['^', dots]), ZeroOrMore(
        [zero_or_more, path_element], '.'), [
        zero_or_more, path_element]


def rrel():
    return path, EOF
