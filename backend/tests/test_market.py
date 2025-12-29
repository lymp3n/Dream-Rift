"""Tests for market system."""

import pytest
from backend.src.models import OrderType, OrderStatus


def test_order_types():
    """Test order type enum."""
    assert OrderType.BUY.value == "buy"
    assert OrderType.SELL.value == "sell"


def test_order_status():
    """Test order status enum."""
    assert OrderStatus.PENDING.value == "pending"
    assert OrderStatus.FILLED.value == "filled"
    assert OrderStatus.CANCELLED.value == "cancelled"
    assert OrderStatus.PARTIAL.value == "partial"

