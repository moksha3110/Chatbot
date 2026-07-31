"""
A calculator tool — safe arithmetic evaluation.

LLMs are famously unreliable at arithmetic, so giving them a real calculator is
genuinely useful. But we must NEVER use Python's eval() on model/user input —
that would let arbitrary code run. Instead we parse the expression into a
syntax tree (ast) and walk it, allowing ONLY numbers and basic math operators.
"""

import ast
import operator

from app.tools.base import Tool

# The only operations we permit.
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and + - * / % ** are allowed")


def _calculate(args: dict) -> str:
    expression = (args.get("expression") or "").strip()
    if not expression:
        return "Error: no expression provided."
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval(tree.body))
    except Exception as e:
        return f"Error: could not evaluate '{expression}': {e}"


calculator_tool = Tool(
    name="calculate",
    description=(
        "Evaluate a mathematical expression (supports + - * / % ** and "
        "parentheses). Use this for any arithmetic instead of computing it yourself."
    ),
    run=_calculate,
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The math expression, e.g. '12 * (3 + 4)'.",
            }
        },
        "required": ["expression"],
    },
)
