"""
FARADAY AI - Function Registry
Central registry for function calling / tools
"""

from typing import Dict, List, Callable, Any, Optional
from functools import wraps
import inspect

from utils.logger import logger


class FunctionRegistry:
    """
    Central registry for function calling.
    Manages tool registration and discovery.
    """

    def __init__(self):
        """Initialize function registry"""
        self._functions: Dict[str, Callable] = {}
        self._function_schemas: Dict[str, Dict[str, Any]] = {}
        logger.info("🔧 Function Registry initialized")

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator to register a function.

        Args:
            name: Function name (optional, uses function __name__ if not provided)
            description: Function description
            parameters: JSON Schema for parameters

        Example:
            @function_registry.register(
                name="web_search",
                description="Search the web for information",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            )
            async def web_search(query: str) -> dict:
                # Implementation
                pass
        """
        def decorator(func: Callable):
            func_name = name or func.__name__
            func_description = description or func.__doc__ or "No description provided"

            # Auto-generate parameters schema if not provided
            func_parameters = parameters
            if func_parameters is None:
                func_parameters = self._generate_schema_from_signature(func)

            # Register function
            self._functions[func_name] = func
            self._function_schemas[func_name] = {
                "name": func_name,
                "description": func_description,
                "parameters": func_parameters
            }

            logger.info(f"✅ Registered function: {func_name}")

            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def _generate_schema_from_signature(self, func: Callable) -> Dict[str, Any]:
        """Auto-generate JSON Schema from function signature"""
        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue

            param_type = "string"  # Default
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == List:
                    param_type = "array"
                elif param.annotation == dict or param.annotation == Dict:
                    param_type = "object"

            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def get_function(self, name: str) -> Optional[Callable]:
        """Get function by name"""
        return self._functions.get(name)

    def get_all_functions(self) -> Dict[str, Callable]:
        """Get all registered functions"""
        return self._functions.copy()

    def get_function_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get function schema by name"""
        return self._function_schemas.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get all function schemas (for OpenAI function calling)"""
        return list(self._function_schemas.values())

    def is_registered(self, name: str) -> bool:
        """Check if function is registered"""
        return name in self._functions

    async def call(self, name: str, **kwargs) -> Any:
        """
        Call a registered function.

        Args:
            name: Function name
            **kwargs: Function arguments

        Returns:
            Function result
        """
        func = self.get_function(name)
        if func is None:
            raise ValueError(f"Function '{name}' not registered")

        try:
            logger.info(f"🔧 Calling function: {name}")
            result = await func(**kwargs)
            logger.info(f"✅ Function '{name}' completed")
            return result
        except Exception as e:
            logger.error(f"❌ Error calling function '{name}': {e}")
            raise

    def list_functions(self) -> List[str]:
        """List all registered function names"""
        return list(self._functions.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_functions": len(self._functions),
            "registered_functions": self.list_functions()
        }

    def print_registry(self):
        """Print all registered functions"""
        print("\n" + "="*60)
        print("🔧 Function Registry")
        print("="*60)

        if not self._functions:
            print("No functions registered.")
        else:
            for name, schema in self._function_schemas.items():
                print(f"\n📌 {name}")
                print(f"   Description: {schema['description']}")
                if schema['parameters']['properties']:
                    print("   Parameters:")
                    for param_name, param_info in schema['parameters']['properties'].items():
                        required = " (required)" if param_name in schema['parameters'].get('required', []) else ""
                        print(f"     - {param_name}: {param_info['type']}{required}")

        print("\n" + "="*60 + "\n")


# Global registry instance
function_registry = FunctionRegistry()


# Convenience decorator
def register_function(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
):
    """
    Convenience decorator for registering functions.

    Example:
        @register_function(
            description="Search the web",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        )
        async def web_search(query: str) -> dict:
            pass
    """
    return function_registry.register(name=name, description=description, parameters=parameters)


# Export
__all__ = ['FunctionRegistry', 'function_registry', 'register_function']
