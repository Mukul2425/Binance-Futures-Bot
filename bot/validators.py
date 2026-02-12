from __future__ import annotations

from typing import Literal, Tuple


Side = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT", "STOP_LIMIT"]


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
    if t not in ("MARKET", "LIMIT", "STOP_LIMIT"):
        raise ValidationError("Order type must be one of: MARKET, LIMIT, STOP_LIMIT.")
    return t  # type: ignore[return-value]


def validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return quantity


def _validate_positive(name: str, value: float) -> float:
    if value <= 0:
        raise ValidationError(f"{name} must be greater than 0.")
    return value


def validate_price_and_stop_price(
    order_type: OrderType, price: float | None, stop_price: float | None
) -> Tuple[float | None, float | None]:
    """
    Validate price/stopPrice combinations for supported order types.
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        return _validate_positive("Price", price), None

    if order_type == "STOP_LIMIT":
        if price is None:
            raise ValidationError("Price is required for STOP_LIMIT orders.")
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        return (
            _validate_positive("Price", price),
            _validate_positive("Stop price", stop_price),
        )

    # MARKET
    return None, None


def validate_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
    stop_price: float | None,
) -> Tuple[str, Side, OrderType, float, float | None, float | None]:
    """
    Validate and normalize all core order fields from CLI.
    Returns normalized values.
    """
    norm_symbol = normalize_symbol(symbol)
    norm_side = normalize_side(side)
    norm_type = normalize_order_type(order_type)
    norm_qty = validate_quantity(quantity)
    norm_price, norm_stop_price = validate_price_and_stop_price(
        norm_type, price, stop_price
    )
    return norm_symbol, norm_side, norm_type, norm_qty, norm_price, norm_stop_price

