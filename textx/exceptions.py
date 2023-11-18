class TextXError(Exception):
    def __init__(
        self,
        message,
        line=None,
        col=None,
        nchar=None,
        err_type=None,
        filename=None,
        context=None
    ):
        super().__init__(message.encode("utf-8"))
        self.line = line
        self.col = col
        self.nchar = nchar
        self.err_type = err_type
        self.filename = filename
        self.message = message
        self.context = context

    def __str__(self):
        if self.line or self.col or self.filename:
            # gcc style error format
            return "{}:{}:{}: {}{}".format(
                str(self.filename),
                str(self.line),
                str(self.col),
                self.message,
                f" => '{self.context}'" if self.context else "",
            )
        else:
            return super().__str__()


class TextXSemanticError(TextXError):
    def __init__(
        self,
        message,
        line=None,
        col=None,
        nchar=None,
        err_type=None,
        expected_obj_cls=None,
        filename=None,
        context=None,
    ):
        super().__init__(message, line, col, nchar, err_type, filename, context)
        # Expected object of class
        self.expected_obj_cls = expected_obj_cls


class TextXSyntaxError(TextXError):
    def __init__(
        self,
        message,
        line=None,
        col=None,
        nchar=None,
        err_type=None,
        expected_rules=None,
        filename=None,
        context=None,
    ):
        super().__init__(message, line, col, nchar, err_type, filename, context)
        # Possible rules on this position
        self.expected_rules = expected_rules


class TextXRegistrationError(TextXError):
    def __init__(self, message):
        super().__init__(message)
