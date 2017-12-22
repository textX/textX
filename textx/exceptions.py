# TextX Exceptions
class TextXError(Exception):
    def __init__(self, message, line=None, col=None):
        super(TextXError, self).__init__(message.encode('utf-8'))
        self.line = line
        self.col = col


class TextXSemanticError(TextXError):
    pass


class TextXSyntaxError(TextXError):
    pass
