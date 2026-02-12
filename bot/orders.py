from __future__ import annotations

import logging
from typing import Any, Dict

from .client import BinanceFuturesClient, OrderResult
from .validators import (
    ValidationError,
    validate_order_request,
)

logger = logging.getLogger(__name__)


def place_order_with_validation(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None,
) -> OrderResult:
    """
    Validate user input, log request summary, and place an order via the client.

    Raises:
        ValidationError, BinanceApiError, BinanceNetworkError, ValueError
    """
    norm_symbol, norm_side, norm_type, norm_qty, norm_price = validate_order_request(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )

    request_summary: Dict[str, Any] = {
        "symbol": norm_symbol,
        "side": norm_side,
        "type": norm_type,
        "quantity": norm_qty,
    }
    if norm_type == "LIMIT":
        request_summary["price"] = norm_price
        request_summary["timeInForce"] = "GTC"

    logger.info("Placing order: %s", request_summary)

    result = client.place_order(
        symbol=norm_symbol,
        side=norm_side,
        order_type=norm_type,
        quantity=norm_qty,
        price=norm_price,
        time_in_force="GTC",
    )

    logger.info(
        "Order placed successfully: orderId=%s status=%s executedQty=%s avgPrice=%s",
        result.order_id,
        result.status,
        result.executed_qty,
        result.avg_price,
    )

    return result

