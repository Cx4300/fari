"""
FARADAY AI - Calculator Tool
Mathematical calculations and expression evaluation
"""

from typing import Dict, Any, Union
import math
import re

from tools.function_registry import register_function
from config.settings import settings
from utils.logger import logger


@register_function(
    name="calculator",
    description="Perform mathematical calculations. Supports basic arithmetic, trigonometry, logarithms, and complex expressions. Use this for precise numerical calculations.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 2', 'sin(pi/2)', 'sqrt(16)')"
            }
        },
        "required": ["expression"]
    }
)
async def calculator(expression: str) -> Dict[str, Any]:
    """
    Evaluate mathematical expression.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Calculation result
    """
    try:
        logger.info(f"🔢 Calculating: {expression}")

        # Clean expression
        expression = expression.strip()

        # Check if calculator is enabled
        if not settings.is_tool_enabled("calculator"):
            logger.warning("⚠️  Calculator is disabled")
            return {
                "success": False,
                "error": "Calculator is disabled in settings"
            }

        # Evaluate expression
        result = _safe_eval(expression)

        # Format result
        precision = settings.tools.calculator_precision

        if isinstance(result, float):
            if result.is_integer():
                formatted_result = int(result)
            else:
                formatted_result = round(result, precision)
        else:
            formatted_result = result

        logger.info(f"✅ Result: {formatted_result}")

        return {
            "success": True,
            "expression": expression,
            "result": formatted_result,
            "formatted": str(formatted_result)
        }

    except ZeroDivisionError:
        logger.error("❌ Division by zero")
        return {
            "success": False,
            "expression": expression,
            "error": "Division by zero"
        }
    except SyntaxError as e:
        logger.error(f"❌ Invalid expression: {e}")
        return {
            "success": False,
            "expression": expression,
            "error": f"Invalid expression: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Calculation error: {e}")
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }


def _safe_eval(expression: str) -> Union[int, float]:
    """
    Safely evaluate mathematical expression.
    Uses a whitelist of allowed functions.
    """
    # Allowed functions and constants
    safe_dict = {
        # Math functions
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow,

        # Math module functions
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'floor': math.floor,
        'ceil': math.ceil,
        'trunc': math.trunc,
        'degrees': math.degrees,
        'radians': math.radians,
        'factorial': math.factorial,
        'gcd': math.gcd,

        # Constants
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
        'nan': math.nan,
    }

    # Replace common mathematical notation
    expression = _preprocess_expression(expression)

    # Evaluate using safe dictionary
    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return result
    except Exception as e:
        raise SyntaxError(f"Invalid expression: {str(e)}")


def _preprocess_expression(expression: str) -> str:
    """Preprocess expression to handle common mathematical notation"""

    # Replace ^ with **
    expression = expression.replace('^', '**')

    # Replace common constants
    replacements = {
        'π': 'pi',
        '√': 'sqrt',
    }

    for old, new in replacements.items():
        expression = expression.replace(old, new)

    # Handle implicit multiplication (e.g., "2pi" -> "2*pi")
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)
    expression = re.sub(r'(\))(\d)', r'\1*\2', expression)
    expression = re.sub(r'(\d)(\()', r'\1*\2', expression)

    return expression


# Convenience functions for common calculations

@register_function(
    name="percentage",
    description="Calculate percentage. For example: 'What is 20% of 150?'",
    parameters={
        "type": "object",
        "properties": {
            "percentage": {"type": "number", "description": "Percentage value"},
            "of_value": {"type": "number", "description": "Base value"}
        },
        "required": ["percentage", "of_value"]
    }
)
async def percentage(percentage: float, of_value: float) -> Dict[str, Any]:
    """Calculate percentage of a value"""
    try:
        result = (percentage / 100) * of_value
        return {
            "success": True,
            "percentage": percentage,
            "of_value": of_value,
            "result": result,
            "formatted": f"{percentage}% of {of_value} = {result}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Export
__all__ = ['calculator', 'percentage']
