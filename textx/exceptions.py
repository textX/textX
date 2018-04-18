# TextX Exceptions
class TextXError(Exception):
    def __init__(self, message, line=None, col=None,
                 err_type=None, filename=None):
        super(TextXError, self).__init__(message.encode('utf-8'))
        self.line = line
        self.col = col
        self.err_type = err_type
        self.filename = filename
        self.message = message

    def __str__(self):
        if self.line or self.col or self.filename:
            # gcc style error format
            return "{}:{}:{}: error: {}".format(
                str(self.filename),
                str(self.line),
                str(self.col),
                self.message
            )
        else:
            return super(TextXError, self).__str__()


class TextXSemanticError(TextXError):
    def __init__(self, message, line=None, col=None, err_type=None,
                 expected_obj_cls=None, filename=None):
        super(TextXSemanticError, self).__init__(
            message, line, col, err_type, filename)
        # Expected object of class
        self.expected_obj_cls = expected_obj_cls


class TextXSyntaxError(TextXError):
    def __init__(self, message, line=None, col=None, err_type=None,
                 expected_rules=None, filename=None):
        super(TextXSyntaxError, self).__init__(
            message, line, col, err_type, filename)
        # Possible rules on this position
        self.expected_rules = expected_rules
