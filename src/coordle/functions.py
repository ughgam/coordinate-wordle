# src/coordle/functions.py

import ast
import math
from typing import Callable, Any


_ALLOWED_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "log": math.log,
    "sqrt": math.sqrt,
    "abs": abs,
    "floor": math.floor,
    "ceil": math.ceil,
}

_ALLOWED_NAMES = {
    **_ALLOWED_FUNCS,
}


class FunctionParseError(Exception):
    """Raised when the expression is not allowed or cannot be parsed."""
    pass


class SafeEvaluator(ast.NodeVisitor):
    """
    Evaluates a restricted expression AST for a given x.

    Only supports:
      - literals (int/float)
      - Name 'x'
      - allowed function calls (sin, cos, ...)
      - binary ops: +, -, *, /, **
      - unary ops: +, -
      - conditional expression (a if cond else b) – optional, limited
    """

    def __init__(self, expr: str):
        self.expr = expr
        try:
            self.tree = ast.parse(expr, mode="eval")
        except SyntaxError as e:
            raise FunctionParseError(f"Syntax error in expression: {e}") from e

        # Validate structure
        self._validate(self.tree)

    # --- validation ---

    def _validate(self, node: ast.AST) -> None:
        """Walk AST and ensure only allowed nodes appear."""
        if isinstance(node, ast.Expression):
            self._validate(node.body)

        elif isinstance(node, ast.BinOp):
            if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                raise FunctionParseError(f"Operator {type(node.op).__name__} not allowed")
            self._validate(node.left)
            self._validate(node.right)

        elif isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, (ast.UAdd, ast.USub)):
                raise FunctionParseError(f"Unary operator {type(node.op).__name__} not allowed")
            self._validate(node.operand)

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise FunctionParseError("Only direct function names are allowed")
            func_name = node.func.id
            if func_name not in _ALLOWED_FUNCS:
                raise FunctionParseError(f"Function '{func_name}' is not allowed")
            for arg in node.args:
                self._validate(arg)
            if node.keywords:
                raise FunctionParseError("Keyword arguments are not allowed")

        elif isinstance(node, ast.Name):
            if node.id != "x":
                raise FunctionParseError(f"Unknown name '{node.id}'")

        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise FunctionParseError("Only int/float constants are allowed")

        elif isinstance(node, ast.IfExp):
            # a if cond else b
            # We allow only very simple conditions: comparisons with x & constants
            self._validate(node.body)
            self._validate(node.orelse)
            self._validate_condition(node.test)

        else:
            raise FunctionParseError(f"Node type {type(node).__name__} not allowed")

    def _validate_condition(self, node: ast.AST) -> None:
        """Very limited validation for a boolean expression."""
        if isinstance(node, ast.Compare):
            # x < 3, x >= -2, etc.
            self._validate(node.left)
            for comparator in node.comparators:
                self._validate(comparator)
            for op in node.ops:
                if not isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)):
                    raise FunctionParseError(f"Comparison operator {type(op).__name__} not allowed")
        elif isinstance(node, ast.BoolOp):
            # and/or of comparisons
            if not isinstance(node.op, (ast.And, ast.Or)):
                raise FunctionParseError(f"Bool op {type(node.op).__name__} not allowed")
            for val in node.values:
                self._validate_condition(val)
        else:
            raise FunctionParseError(f"Condition node {type(node).__name__} not allowed")

    # --- evaluation ---

    def _eval(self, node: ast.AST, x_value: float) -> Any:
        if isinstance(node, ast.Expression):
            return self._eval(node.body, x_value)

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id == "x":
                return x_value
            raise FunctionParseError(f"Unknown name '{node.id}' during evaluation")

        if isinstance(node, ast.BinOp):
            left = self._eval(node.left, x_value)
            right = self._eval(node.right, x_value)
            op = node.op
            if isinstance(op, ast.Add):
                return left + right
            if isinstance(op, ast.Sub):
                return left - right
            if isinstance(op, ast.Mult):
                return left * right
            if isinstance(op, ast.Div):
                return left / right
            if isinstance(op, ast.Pow):
                return left ** right
            raise FunctionParseError(f"Unexpected operator {type(op).__name__}")

        if isinstance(node, ast.UnaryOp):
            operand = self._eval(node.operand, x_value)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise FunctionParseError(f"Unexpected unary operator {type(node.op).__name__}")

        if isinstance(node, ast.Call):
            func_name = node.func.id
            func = _ALLOWED_FUNCS[func_name]
            args = [self._eval(a, x_value) for a in node.args]
            return func(*args)

        if isinstance(node, ast.IfExp):
            cond_val = self._eval_cond(node.test, x_value)
            if cond_val:
                return self._eval(node.body, x_value)
            else:
                return self._eval(node.orelse, x_value)

        raise FunctionParseError(f"Unexpected node type {type(node).__name__}")

    def _eval_cond(self, node: ast.AST, x_value: float) -> bool:
        if isinstance(node, ast.Compare):
            left = self._eval(node.left, x_value)
            # Only simple comparisons like left < right1 < right2 ...
            result = True
            current_left = left
            for op, comp in zip(node.ops, node.comparators):
                right = self._eval(comp, x_value)
                if isinstance(op, ast.Lt):
                    result = result and (current_left < right)
                elif isinstance(op, ast.LtE):
                    result = result and (current_left <= right)
                elif isinstance(op, ast.Gt):
                    result = result and (current_left > right)
                elif isinstance(op, ast.GtE):
                    result = result and (current_left >= right)
                elif isinstance(op, ast.Eq):
                    result = result and (current_left == right)
                elif isinstance(op, ast.NotEq):
                    result = result and (current_left != right)
                current_left = right
            return result

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_cond(v, x_value) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(self._eval_cond(v, x_value) for v in node.values)
            raise FunctionParseError(f"Unexpected BoolOp {type(node.op).__name__}")

        raise FunctionParseError(f"Unexpected condition node {type(node).__name__}")

    def make_callable(self) -> Callable[[float], float]:
        """Return a Python callable f(x) evaluating this expression."""
        def f(x: float) -> float:
            return float(self._eval(self.tree, x))
        return f


def build_function(expr: str) -> Callable[[float], float]:
    """
    Parse and return a safe callable f(x) from a user expression.
    Raises FunctionParseError on invalid input.
    """
    evaluator = SafeEvaluator(expr)
    return evaluator.make_callable()
