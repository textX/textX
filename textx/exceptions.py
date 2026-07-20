from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class TextXError(Exception):
    def __init__(
        self,
        message: str,
        line: int | None = None,
        col: int | None = None,
        nchar: int | None = None,
        err_type: str | None = None,
        filename: str | None = None,
        context: str | None = None,
    ) -> None:
        super().__init__(message)
        self.line = line
        self.col = col
        self.nchar = nchar
        self.err_type = err_type
        self.filename = filename
        self.message = message
        self.context = context

    def __str__(self) -> str:
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
        message: str,
        line: int | None = None,
        col: int | None = None,
        nchar: int | None = None,
        err_type: str | None = None,
        expected_obj_cls: type[Any] | None = None,
        filename: str | None = None,
        context: str | None = None,
    ) -> None:
        super().__init__(message, line, col, nchar, err_type, filename, context)
        # Expected object of class
        self.expected_obj_cls = expected_obj_cls


class TextXSyntaxError(TextXError):
    def __init__(
        self,
        message: str,
        line: int | None = None,
        col: int | None = None,
        nchar: int | None = None,
        err_type: str | None = None,
        expected_rules: Iterable[str] | None = None,
        filename: str | None = None,
        context: str | None = None,
    ) -> None:
        super().__init__(message, line, col, nchar, err_type, filename, context)
        # Possible rules on this position
        self.expected_rules = expected_rules


class TextXRegistrationError(TextXError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
