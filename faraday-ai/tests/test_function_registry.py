"""
Test Function Registry
"""

import pytest
from tools.function_registry import FunctionRegistry


@pytest.fixture
def registry():
    """Create fresh registry for each test"""
    return FunctionRegistry()


def test_register_function(registry):
    """Test function registration"""

    @registry.register(name="test_func", description="Test function")
    async def test_func(x: int) -> int:
        return x * 2

    assert registry.is_registered("test_func")
    assert len(registry.list_functions()) >= 1


def test_get_function(registry):
    """Test getting registered function"""

    @registry.register(name="add", description="Add two numbers")
    async def add(a: int, b: int) -> int:
        return a + b

    func = registry.get_function("add")
    assert func is not None
    assert callable(func)


@pytest.mark.asyncio
async def test_call_function(registry):
    """Test calling registered function"""

    @registry.register(name="multiply")
    async def multiply(a: int, b: int) -> int:
        return a * b

    result = await registry.call("multiply", a=5, b=3)
    assert result == 15


def test_function_schema(registry):
    """Test function schema generation"""

    @registry.register(
        name="greet",
        description="Greet someone",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
    )
    async def greet(name: str) -> str:
        return f"Hello, {name}!"

    schema = registry.get_function_schema("greet")
    assert schema is not None
    assert schema["name"] == "greet"
    assert schema["description"] == "Greet someone"
    assert "name" in schema["parameters"]["properties"]


def test_list_functions(registry):
    """Test listing all functions"""

    @registry.register(name="func1")
    async def func1():
        pass

    @registry.register(name="func2")
    async def func2():
        pass

    functions = registry.list_functions()
    assert "func1" in functions
    assert "func2" in functions


def test_get_all_schemas(registry):
    """Test getting all schemas"""

    @registry.register(name="test1")
    async def test1():
        pass

    @registry.register(name="test2")
    async def test2():
        pass

    schemas = registry.get_all_schemas()
    assert len(schemas) >= 2
    assert all("name" in s for s in schemas)
