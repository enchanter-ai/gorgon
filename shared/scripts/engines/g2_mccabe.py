"""
G2 — McCabe Cyclomatic Complexity

Reference:
    McCabe T.J. (1976), "A Complexity Measure",
    IEEE Transactions on Software Engineering SE-2(4):308-320.

Role:
    Per-function complexity from the count of decision points in the AST.
    M = E - N + 2 over the control-flow graph; equivalent to (decision points + 1)
    for a connected single-entry/single-exit function body.

Stdlib only: walks Python `ast` module nodes.
"""
from __future__ import annotations

import ast


_DECISION_NODES = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.Try,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncWith,
    ast.IfExp,
    ast.Assert,
    ast.comprehension,
)


def _count_decision_points(node: ast.AST) -> int:
    count = 0
    for child in ast.walk(node):
        if isinstance(child, _DECISION_NODES):
            count += 1
        elif isinstance(child, ast.BoolOp):
            # Each additional operand in a chain adds a branch.
            count += max(0, len(child.values) - 1)
    return count


def cyclomatic(tree: ast.AST) -> dict:
    """Return {qualified_function_name: complexity}.

    A module's free-floating top-level statements are not counted; we score
    function and method bodies. Lambda is folded into its enclosing scope.
    """
    scores: dict = {}

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qname = f"{prefix}{child.name}" if prefix else child.name
                scores[qname] = 1 + _count_decision_points(child)
                visit(child, qname + ".")
            elif isinstance(child, ast.ClassDef):
                visit(child, f"{prefix}{child.name}.")
            else:
                visit(child, prefix)

    visit(tree, "")
    return scores
