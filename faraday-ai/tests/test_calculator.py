"""
Test Calculator Tool
"""

import pytest
from tools.calculator import calculator, percentage


@pytest.mark.asyncio
async def test_calculator_basic():
    """Test basic arithmetic"""
    result = await calculator("2 + 2")
    assert result["success"] is True
    assert result["result"] == 4


@pytest.mark.asyncio
async def test_calculator_complex():
    """Test complex expression"""
    result = await calculator("(10 + 5) * 2 - 3")
    assert result["success"] is True
    assert result["result"] == 27


@pytest.mark.asyncio
async def test_calculator_math_functions():
    """Test math functions"""
    result = await calculator("sqrt(16)")
    assert result["success"] is True
    assert result["result"] == 4.0


@pytest.mark.asyncio
async def test_percentage():
    """Test percentage calculation"""
    result = await percentage(20, 150)
    assert result["success"] is True
    assert result["result"] == 30.0


@pytest.mark.asyncio
async def test_calculator_division_by_zero():
    """Test division by zero"""
    result = await calculator("10 / 0")
    assert result["success"] is False
    assert "Division by zero" in result["error"]


@pytest.mark.asyncio
async def test_calculator_invalid_expression():
    """Test invalid expression"""
    result = await calculator("2 ++ 2")
    assert result["success"] is False
