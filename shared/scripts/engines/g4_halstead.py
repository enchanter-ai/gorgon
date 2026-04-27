"""
G4 — Halstead Volume Metrics

Reference:
    Halstead M.H. (1977), "Elements of Software Science",
    Elsevier North-Holland.

Role:
    Per-module Halstead metrics. Volume V = (N1 + N2) * log2(n1 + n2) where:
        n1 = distinct operators
        n2 = distinct operands
        N1 = total operator occurrences
        N2 = total operand occurrences
    Complementary to G2 — Halstead catches dense data-shuffling code that
    McCabe under-weights.

Stdlib only: `tokenize` for token classification + `math.log2`.
"""
from __future__ import annotations

import io
import math
import token as _tok
import tokenize


# Operator-bearing token types in Python's tokenize stream.
_OPERATOR_TYPES = {_tok.OP}
# Treat keywords as operators (Halstead's classical mapping for control flow).
_KEYWORD_OPS = {
    "if", "elif", "else", "for", "while", "try", "except", "finally",
    "with", "as", "return", "yield", "break", "continue", "pass",
    "import", "from", "raise", "and", "or", "not", "is", "in",
    "lambda", "def", "class", "global", "nonlocal", "assert", "del",
    "async", "await",
}


def halstead(source: str) -> dict:
    """Return {n1, n2, N1, N2, vocabulary, length, volume} for the source string.

    On tokenize failure (syntax error, encoding glitch), returns zeros — fail-open.
    """
    operators: dict = {}
    operands: dict = {}
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return {
            "n1": 0, "n2": 0, "N1": 0, "N2": 0,
            "vocabulary": 0, "length": 0, "volume": 0.0,
        }

    for tok in tokens:
        ttype = tok.type
        tstr = tok.string
        if ttype in (_tok.ENCODING, _tok.NEWLINE, _tok.NL,
                     _tok.INDENT, _tok.DEDENT, _tok.ENDMARKER,
                     _tok.COMMENT):
            continue
        if ttype in _OPERATOR_TYPES:
            operators[tstr] = operators.get(tstr, 0) + 1
        elif ttype == _tok.NAME:
            if tstr in _KEYWORD_OPS:
                operators[tstr] = operators.get(tstr, 0) + 1
            else:
                operands[tstr] = operands.get(tstr, 0) + 1
        elif ttype in (_tok.NUMBER, _tok.STRING, _tok.FSTRING_START,
                       _tok.FSTRING_MIDDLE, _tok.FSTRING_END):
            operands[tstr] = operands.get(tstr, 0) + 1

    n1 = len(operators)
    n2 = len(operands)
    N1 = sum(operators.values())
    N2 = sum(operands.values())
    vocabulary = n1 + n2
    length = N1 + N2
    if vocabulary <= 1:
        volume = 0.0
    else:
        volume = length * math.log2(vocabulary)
    return {
        "n1": n1, "n2": n2, "N1": N1, "N2": N2,
        "vocabulary": vocabulary, "length": length, "volume": float(volume),
    }
