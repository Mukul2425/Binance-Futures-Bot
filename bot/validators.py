from __future__ import annotations

from typing import Literal, Tuple


Side = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT"]


class ValidationError(Exception):
    """Raised when CLI/user input is invalid."""


def normalize_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not s:
        raise ValidationError("Symbol must not be empty.")
    return s


def normalize_side(side: str) -> Side:
    s = side.strip().upper()
    if s not in ("BUY", "SELL"):
        raise ValidationError("Side must be either BUY or SELL.")
    return s  # type: ignore[return-value]


def normalize_order_type(order_type: str) -> OrderType:
    t = order_type.strip().upper()
    if t not in ("MARKET", "LIMIT"):
        raise ValidationError("Order type must be either MARKET or LIMIT.")
    return t  # type: ignore[return-value]


def validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return quantity


def validate_price_for_limit(order_type: OrderType, price: float | None) -> float | None:
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price
    return None


def validate_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
) -> Tuple[str, Side, OrderType, float, float | None]:
    """
    Validate and normalize all core order fields from CLI.
    Returns normalized values.
    """
    norm_symbol = normalize_symbol(symbol)
    norm_side = normalize_side(side)
    norm_type = normalize_order_type(order_type)
    norm_qty = validate_quantity(quantity)
    norm_price = validate_price_for_limit(norm_type, price)
    return norm_symbol, norm_side, norm_type, norm_qty, norm_price

