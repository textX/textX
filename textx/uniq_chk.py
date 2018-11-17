import textx
from textx.exceptions import TextXSemanticError


def uniq_chk(obj, attr_name):
    """
    Checks if 'obj' children in attribute with name 'attr_name' are unique
    w.r.t to their name attribute. If not, throws a semantic error with source
    info of both childrens. Can be useful for checking for multiple definitions

    """

    # TODO does not work with imports nor fqn providers yet
    m = textx.get_model(obj)

    def obj_src_info(obj):
        """Returns object's line, col and filename"""
        line, col = m._tx_parser.pos_to_linecol(obj._tx_position)
        return line, col, m._tx_filename

    def scan_siblings(siblings):
        for p in siblings:
            for q in siblings:
                if p == q:
                    break

                if p.name == q.name:
                    line, col, filename = obj_src_info(p)
                    orig_line, orig_col, orig_filename = obj_src_info(q)

                    msg = "'{}' already defined, previously seen at {}:{}:{}"\
                        .format(p.name, orig_filename, orig_line, orig_col)
                    raise TextXSemanticError(msg, line=line, col=col,
                                             filename=filename)

    cls = obj.__class__
    if hasattr(cls, '_tx_attrs'):
        attr = cls._tx_attrs[attr_name]
        if attr and attr.cont:
            siblings = getattr(obj, attr_name)
            scan_siblings(siblings)
