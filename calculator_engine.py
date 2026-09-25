"""
Calculator Engine Module
Handles mathematical evaluations, trigonometric angle conversions,
scientific functions, and bitwise logical operations safely.
"""

import ast
import math
import re
from typing import Any, Union


class CalculatorEngine:
    """
    Engine responsible for evaluating mathematical and logical expressions safely.
    Supports DEG, RAD, and GRAD angle modes, custom precision, and bitwise operations.
    """

    ANGLE_DEG = "DEG"
    ANGLE_RAD = "RAD"
    ANGLE_GRAD = "GRAD"

    def __init__(self, angle_unit: str = ANGLE_DEG, precision: int = 10):
        self.angle_unit = angle_unit
        self.precision = precision

    def set_angle_unit(self, unit: str) -> None:
        if unit in (self.ANGLE_DEG, self.ANGLE_RAD, self.ANGLE_GRAD):
            self.angle_unit = unit
        else:
            raise ValueError(f"Invalid angle unit: {unit}")

    def set_precision(self, precision: int) -> None:
        if 0 <= precision <= 20:
            self.precision = precision

    def _to_radians(self, val: float) -> float:
        if self.angle_unit == self.ANGLE_DEG:
            return math.radians(val)
        elif self.angle_unit == self.ANGLE_GRAD:
            return val * math.pi / 200.0
        return val  # RAD

    def _from_radians(self, rad_val: float) -> float:
        if self.angle_unit == self.ANGLE_DEG:
            return math.degrees(rad_val)
        elif self.angle_unit == self.ANGLE_GRAD:
            return rad_val * 200.0 / math.pi
        return rad_val  # RAD

    # Trigonometric functions respecting current angle unit
    def sin(self, x: float) -> float:
        return math.sin(self._to_radians(x))

    def cos(self, x: float) -> float:
        return math.cos(self._to_radians(x))

    def tan(self, x: float) -> float:
        rad = self._to_radians(x)
        # Handle tan(90 deg) or equivalent where cos is ~0
        if abs(math.cos(rad)) < 1e-15:
            raise ValueError("Tangent undefined (division by zero)")
        return math.tan(rad)

    def asin(self, x: float) -> float:
        if x < -1 or x > 1:
            raise ValueError("Domain error for asin")
        return self._from_radians(math.asin(x))

    def acos(self, x: float) -> float:
        if x < -1 or x > 1:
            raise ValueError("Domain error for acos")
        return self._from_radians(math.acos(x))

    def atan(self, x: float) -> float:
        return self._from_radians(math.atan(x))

    def log10(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Domain error for log10")
        return math.log10(x)

    def ln(self, x: float) -> float:
        if x <= 0:
            raise ValueError("Domain error for ln")
        return math.log(x)

    def sqrt(self, x: float) -> float:
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(x)

    def factorial(self, x: float) -> int:
        if x < 0 or not float(x).is_integer():
            raise ValueError("Factorial requires a non-negative integer")
        return math.factorial(int(x))

    def preprocess_expression(self, expr: str) -> str:
        """
        Preprocesses a user-input expression into python-evaluable syntax.
        """
        expr = expr.strip()
        if not expr:
            return "0"

        # Replace visual symbols
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace("π", "pi").replace("PI", "pi")

        # Convert user power symbol ^ to ** first (before replacing XOR keyword with ^)
        expr = expr.replace("^", "**")

        # Replace logical words
        expr = re.sub(r'\bAND\b', '&', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bOR\b', '|', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bXOR\b', '^', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bNOT\b', '~', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bMOD\b', '%', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bLSH\b', '<<', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bRSH\b', '>>', expr, flags=re.IGNORECASE)

        # Handle implicit multiplication like 2pi -> 2*pi, 3(4) -> 3*(4), 5sin(x) -> 5*sin(x)
        expr = re.sub(r'(\d)(\s*)(pi|e|sin|cos|tan|asin|acos|atan|log|ln|sqrt|\()', r'\1*\3', expr)
        expr = re.sub(r'(\))(\s*)(\d|pi|e|sin|cos|tan|asin|acos|atan|log|ln|sqrt|\()', r'\1*\3', expr)

        # Handle factorials like 5! -> factorial(5)
        expr = re.sub(r'(\d+|\b\w+\b|\))!', r'factorial(\1)', expr)

        return expr

    def evaluate(self, expr: str) -> Union[int, float, str]:
        """
        Safely evaluates an expression string using AST syntax tree parsing.
        """
        try:
            cleaned_expr = self.preprocess_expression(expr)
            parsed = ast.parse(cleaned_expr, mode='eval')
            result = self._eval_node(parsed.body)

            # Round result if float according to precision
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, self.precision)

            return result
        except ZeroDivisionError:
            raise ValueError("Division by zero")
        except OverflowError:
            raise ValueError("Overflow error")
        except Exception as e:
            if str(e):
                raise ValueError(str(e))
            raise ValueError("Invalid expression")

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):  # Numbers, constants
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.Name):
            name = node.id
            if name == "pi":
                return math.pi
            elif name == "e":
                return math.e
            raise ValueError(f"Unknown variable: {name}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.Invert):
                return ~int(operand)
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = node.op

            if isinstance(op, ast.Add):
                return left + right
            elif isinstance(op, ast.Sub):
                return left - right
            elif isinstance(op, ast.Mult):
                return left * right
            elif isinstance(op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError()
                return left / right
            elif isinstance(op, ast.FloorDiv):
                if right == 0:
                    raise ZeroDivisionError()
                return left // right
            elif isinstance(op, ast.Mod):
                if right == 0:
                    raise ZeroDivisionError()
                return left % right
            elif isinstance(op, ast.Pow):
                return left ** right
            elif isinstance(op, ast.BitAnd):
                return int(left) & int(right)
            elif isinstance(op, ast.BitOr):
                return int(left) | int(right)
            elif isinstance(op, ast.BitXor):
                return int(left) ^ int(right)
            elif isinstance(op, ast.LShift):
                return int(left) << int(right)
            elif isinstance(op, ast.RShift):
                return int(left) >> int(right)
            raise ValueError(f"Unsupported binary operator: {type(op)}")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function call")
            func_name = node.func.id
            args = [self._eval_node(arg) for arg in node.args]

            if func_name == "sin":
                return self.sin(args[0])
            elif func_name == "cos":
                return self.cos(args[0])
            elif func_name == "tan":
                return self.tan(args[0])
            elif func_name == "asin":
                return self.asin(args[0])
            elif func_name == "acos":
                return self.acos(args[0])
            elif func_name == "atan":
                return self.atan(args[0])
            elif func_name == "log":
                return self.log10(args[0])
            elif func_name == "ln":
                return self.ln(args[0])
            elif func_name == "sqrt":
                return self.sqrt(args[0])
            elif func_name == "factorial":
                return self.factorial(args[0])
            elif func_name == "abs":
                return abs(args[0])
            raise ValueError(f"Unknown function: {func_name}")

        raise ValueError(f"Unsupported syntax: {type(node)}")

    # Base representations
    @staticmethod
    def to_hex(value: int) -> str:
        return hex(int(value)).upper().replace("0X", "0x")

    @staticmethod
    def to_bin(value: int) -> str:
        return bin(int(value)).replace("0b", "0b")

    @staticmethod
    def to_oct(value: int) -> str:
        return oct(int(value)).replace("0o", "0o")
