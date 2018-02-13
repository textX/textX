# TextX Exceptions
class TextXError(Exception):
    def __init__(self, message, line=None, col=None,
                 err_type=None):
        super(TextXError, self).__init__(message.encode('utf-8'))
        self.line = line
        self.col = col
        self.err_type = err_type


class TextXSemanticError(TextXError):
    def __init__(self, message, line=None, col=None, err_type=None,
                 expected_obj_cls=None):
        super(TextXSemanticError, self).__init__(message, line, col, err_type)
        # Expected object of class
        self.expected_obj_cls = expected_obj_cls


class TextXSyntaxError(TextXError):
    def __init__(self, message, line=None, col=None, err_type=None,
                 expected_rules=None):
        super(TextXSyntaxError, self).__init__(message, line, col, err_type)
        # Possible rules on this position
        self.expected_rules = expected_rules
