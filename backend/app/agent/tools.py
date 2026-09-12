import ast
import json
import math
import operator
from typing import Any, Callable

from ddgs import DDGS


class ToolError(Exception):
    pass


MAX_EXPRESSION_LENGTH = 500
MAX_AST_NODES = 100
MAX_ABS_RESULT = 1e100


def _safe_calculate(expression: str) -> str:
    """Evaluate basic arithmetic without using eval()."""
    expression = expression.strip()
    if not expression:
        raise ToolError("Expression cannot be empty")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ToolError("Expression is too long")

    allowed_binary = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }
    allowed_unary = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError, MemoryError, RecursionError) as exc:
        raise ToolError(f"Invalid calculation: {exc}") from exc

    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise ToolError("Expression is too complex")

    def visit(node: ast.AST) -> int | float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_binary:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ToolError("Exponent is too large")
            result = allowed_binary[type(node.op)](left, right)
            if not math.isfinite(float(result)) or abs(float(result)) > MAX_ABS_RESULT:
                raise ToolError("Calculation result is too large or non-finite")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary:
            result = allowed_unary[type(node.op)](visit(node.operand))
            if not math.isfinite(float(result)) or abs(float(result)) > MAX_ABS_RESULT:
                raise ToolError("Calculation result is too large or non-finite")
            return result
        raise ToolError("Only basic arithmetic is supported")

    try:
        result = visit(tree)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ToolError(f"Invalid calculation: {exc}") from exc

    return str(result)


def _web_search(query: str, max_results: int = 5) -> str:
    """Search the public web and return compact, model-readable results."""
    query = query.strip()
    if not query:
        raise ToolError("Search query cannot be empty")

    max_results = max(1, min(int(max_results), 8))

    try:
        results = list(DDGS().text(query, max_results=max_results))
    except Exception as exc:
        raise ToolError(f"Web search failed: {exc}") from exc

    if not results:
        return json.dumps({"query": query, "results": []})

    compact = []
    for item in results:
        compact.append(
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
            }
        )

    return json.dumps({"query": query, "results": compact}, ensure_ascii=False)


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a basic arithmetic expression exactly. Use this instead of mental math for arithmetic.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the public web for current or unknown information. Use this when the answer may be newer than the model's knowledge or when sources would improve confidence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A concise web search query using important keywords.",
                    },
                    "max_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 8,
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
]

TOOL_FUNCTIONS: dict[str, Callable[..., str]] = {
    "calculate": _safe_calculate,
    "web_search": _web_search,
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
        return json.dumps({"result": result}, ensure_ascii=False)
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError(f"Tool execution failed: {exc}") from exc
