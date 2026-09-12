import ast
import json
import operator
from typing import Any, Callable


class ToolError(Exception):
    pass


def _safe_calculate(expression: str) -> str:
    """Evaluate basic arithmetic without using eval()."""
    allowed_binary = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }
    allowed_unary = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_binary:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ToolError("Exponent is too large")
            return allowed_binary[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary:
            return allowed_unary[type(node.op)](visit(node.operand))
        raise ToolError("Only basic arithmetic is supported")

    try:
        tree = ast.parse(expression, mode="eval")
        result = visit(tree)
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ToolError(f"Invalid calculation: {exc}") from exc

    return str(result)


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a basic arithmetic expression. Use this for exact arithmetic instead of mental math.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A basic arithmetic expression such as (25 * 4) + 10.",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {
    "calculate": _safe_calculate,
}


def execute_tool(name: str, arguments: str | dict[str, Any]) -> str:
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        raise ToolError(f"Unknown tool: {name}")

    try:
        args = json.loads(arguments) if isinstance(arguments, str) else arguments
        if not isinstance(args, dict):
            raise ToolError("Tool arguments must be a JSON object")
        result = function(**args)
        return json.dumps({"result": result})
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError(f"Tool execution failed: {exc}") from exc
