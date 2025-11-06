"""
FARADAY AI - Code Interpreter Tool
Safe Python code execution in sandboxed environment
"""

import asyncio
import sys
import io
import contextlib
from typing import Dict, Any
import traceback

from tools.function_registry import register_function
from config.settings import settings
from utils.logger import logger


# Restricted imports for security
ALLOWED_MODULES = {
    'math', 'statistics', 'random', 'datetime', 'time',
    'json', 're', 'collections', 'itertools', 'functools',
    'numpy', 'pandas', 'matplotlib', 'seaborn',
}

BLOCKED_BUILTINS = {
    'open', 'eval', 'exec', 'compile', '__import__',
    'input', 'file', 'execfile',
}


@register_function(
    name="code_interpreter",
    description="Execute Python code in a sandboxed environment. Useful for calculations, data analysis, and generating visualizations. Returns the output and any generated values.",
    parameters={
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Execution timeout in seconds (default: 30)",
                "default": 30
            }
        },
        "required": ["code"]
    }
)
async def execute_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code in sandboxed environment.

    Args:
        code: Python code to execute
        timeout: Execution timeout in seconds

    Returns:
        Execution result with output, errors, and return value
    """
    try:
        logger.info(f"💻 Executing code ({len(code)} chars)...")

        # Check if code interpreter is enabled
        if not settings.is_tool_enabled("code_interpreter"):
            logger.warning("⚠️  Code interpreter is disabled")
            return {
                "success": False,
                "error": "Code interpreter is disabled in settings"
            }

        # Timeout limit
        if timeout > settings.tools.code_interpreter_timeout:
            timeout = settings.tools.code_interpreter_timeout

        # Execute code with timeout
        try:
            result = await asyncio.wait_for(
                _execute_code_safely(code),
                timeout=timeout
            )
            logger.info("✅ Code execution completed")
            return result

        except asyncio.TimeoutError:
            logger.error(f"❌ Code execution timeout ({timeout}s)")
            return {
                "success": False,
                "error": f"Execution timeout after {timeout} seconds",
                "output": "",
                "return_value": None
            }

    except Exception as e:
        logger.error(f"❌ Code execution error: {e}")
        return {
            "success": False,
            "error": str(e),
            "output": "",
            "return_value": None
        }


async def _execute_code_safely(code: str) -> Dict[str, Any]:
    """Execute code with safety restrictions"""
    try:
        # Capture stdout/stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Create restricted globals
        restricted_globals = {
            '__builtins__': _get_restricted_builtins(),
        }

        # Create locals for execution
        exec_locals = {}

        # Execute in thread pool to avoid blocking
        def _run_code():
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):
                try:
                    # Compile and execute
                    compiled_code = compile(code, '<string>', 'exec')
                    exec(compiled_code, restricted_globals, exec_locals)
                    return True
                except Exception as e:
                    stderr_capture.write(traceback.format_exc())
                    return False

        success = await asyncio.to_thread(_run_code)

        # Get output
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()

        # Get return value (last expression or explicit return)
        return_value = None
        if '_' in exec_locals:
            return_value = exec_locals['_']
        elif exec_locals:
            # Get last defined variable
            last_var = list(exec_locals.values())[-1]
            if not callable(last_var) and not isinstance(last_var, type):
                return_value = last_var

        # Limit output length
        max_length = settings.tools.code_interpreter_max_output_length
        if len(stdout_output) > max_length:
            stdout_output = stdout_output[:max_length] + "\n... (output truncated)"

        result = {
            "success": success and not stderr_output,
            "output": stdout_output,
            "error": stderr_output if stderr_output else None,
            "return_value": str(return_value) if return_value is not None else None,
            "locals": {k: str(v)[:100] for k, v in exec_locals.items() if not k.startswith('_')}
        }

        return result

    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "return_value": None
        }


def _get_restricted_builtins() -> dict:
    """Get restricted builtins dictionary"""
    # Start with safe builtins
    safe_builtins = {
        'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes',
        'chr', 'complex', 'dict', 'divmod', 'enumerate', 'filter',
        'float', 'format', 'frozenset', 'getattr', 'hasattr', 'hash',
        'hex', 'int', 'isinstance', 'issubclass', 'iter', 'len',
        'list', 'map', 'max', 'min', 'next', 'oct', 'ord', 'pow',
        'print', 'range', 'reversed', 'round', 'set', 'setattr',
        'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip',
        'True', 'False', 'None',
    }

    # Get builtin functions
    import builtins
    restricted = {}

    for name in safe_builtins:
        if hasattr(builtins, name):
            restricted[name] = getattr(builtins, name)

    # Add safe modules (lazy import)
    restricted['__import__'] = _restricted_import

    return restricted


def _restricted_import(name, *args, **kwargs):
    """Restricted import function"""
    if name in ALLOWED_MODULES or name.split('.')[0] in ALLOWED_MODULES:
        return __import__(name, *args, **kwargs)
    else:
        raise ImportError(f"Import of '{name}' is not allowed")


# Export
__all__ = ['execute_code']
