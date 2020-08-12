from arpeggio import Optional, EOF
from arpeggio import ZeroOrMore as ArpeggioZeroOrMore
from arpeggio import RegExMatch as _


def id():
    return _(r'[^\d\W]\w*\b')  # from lang.py


def parent():
    return 'parent', '(', id, ')'


def navigation():
    return Optional('~'), id


def brackets():
    return '(', ordered_choice, ')'


def dots():
    return _(r'\.+')


def path_element():
    return [parent, brackets, navigation]


def zero_or_more():
    return path_element, '*'


def path():
    return Optional(['^', dots]), ArpeggioZeroOrMore(
        [zero_or_more, path_element], '.'), Optional([zero_or_more, path_element])


def ordered_choice():
    return ArpeggioZeroOrMore(path, ","), path


def rrel():
    return ordered_choice, EOF
