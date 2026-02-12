"""
Binance Futures Testnet REST client.

Implements just enough of the API to place MARKET, LIMIT, and STOP_LIMIT
orders on USDT-M futures using the testnet base URL:
https://testnet.binancefuture.com
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceApiError(Exception):
    """Represents an error response from the Binance API."""

    def __init__(self, status_code: int, code: Optional[int], msg: str):
        super().__init__(f"Binance API error (status {status_code}, code {code}): {msg}")
        self.status_code = status_code
        self.code = code
        self.msg = msg


class BinanceNetworkError(Exception):
    """Represents a network/transport error talking to Binance."""


@dataclass
class OrderResult:
    order_id: int
    status: str
    executed_qty: str
    avg_price: Optional[str]
    raw: Dict[str, Any]


class BinanceFuturesClient:
    """
    Minimal Binance Futures client for placing orders on the testnet.

    It uses signed requests for trading endpoints and logs requests and responses
    (excluding sensitive secrets).
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        recv_window: int = 5_000,
        timeout: float = 10.0,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.recv_window = recv_window
        self._client = httpx.Client(timeout=timeout)

    def _sign(self, query_string: str) -> str:
        return hmac.new(self.api_secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def _signed_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if params is None:
            params = {}

        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = self.recv_window

        # Build query string in a stable order
        query_items = [f"{k}={params[k]}" for k in sorted(params)]
        query_string = "&".join(query_items)
        signature = self._sign(query_string)
        query_string_with_sig = f"{query_string}&signature={signature}"

        url = f"{self.base_url}{path}"
        headers = {"X-MBX-APIKEY": self.api_key}

        # Log request (without secret, signature)
        logger.info("Sending request to Binance: %s %s?%s", method, url, query_string)

        try:
            if method.upper() == "GET":
                resp = self._client.get(url, params=params, headers=headers)
            else:
                # For Binance Futures, signed trading endpoints accept query params
                # so we keep them in the query string.
                resp = self._client.request(
                    method.upper(), f"{url}?{query_string_with_sig}", headers=headers
                )
        except httpx.HTTPError as exc:
            logger.exception("Network error during Binance request: %s", exc)
            raise BinanceNetworkError(str(exc)) from exc

        logger.info(
            "Received response from Binance: status=%s body=%s",
            resp.status_code,
            resp.text,
        )

        try:
            data = resp.json()
        except ValueError:
            # Non-JSON response
            raise BinanceApiError(resp.status_code, None, f"Non-JSON response: {resp.text}")

        if resp.status_code >= 400:
            code = data.get("code") if isinstance(data, dict) else None
            msg = data.get("msg") if isinstance(data, dict) else resp.text
            raise BinanceApiError(resp.status_code, code, msg)

        if isinstance(data, dict) and "code" in data and data.get("code", 0) != 0:
            # Binance sometimes returns 200 with error code in JSON
            raise BinanceApiError(resp.status_code, data.get("code"), data.get("msg", ""))

        return data

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: Optional[str] = None,
    ) -> OrderResult:
        """
        Place a MARKET, LIMIT, or STOP_LIMIT order on Binance Futures.

        :param symbol: e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param order_type: "MARKET", "LIMIT", or "STOP_LIMIT"
        :param quantity: order quantity
        :param price: required for LIMIT and STOP_LIMIT
        :param stop_price: trigger price for STOP_LIMIT
        :param time_in_force: e.g. "GTC" for LIMIT/STOP_LIMIT orders
        """
        order_type_upper = order_type.upper()
        # Binance Futures uses type=STOP for stop-limit orders
        binance_type = "STOP" if order_type_upper == "STOP_LIMIT" else order_type_upper

        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": binance_type,
            "quantity": quantity,
        }

        if order_type_upper == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders")
            params["price"] = price
            params["timeInForce"] = time_in_force or "GTC"
        elif order_type_upper == "STOP_LIMIT":
            if price is None:
                raise ValueError("price is required for STOP_LIMIT orders")
            if stop_price is None:
                raise ValueError("stop_price is required for STOP_LIMIT orders")
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = time_in_force or "GTC"

        data = self._signed_request("POST", "/fapi/v1/order", params=params)

        order_id = int(data.get("orderId"))
        status = data.get("status", "UNKNOWN")
        executed_qty = data.get("executedQty", "0")
        avg_price = data.get("avgPrice") or data.get("avgPrice", None)

        return OrderResult(
            order_id=order_id,
            status=status,
            executed_qty=executed_qty,
            avg_price=str(avg_price) if avg_price is not None else None,
            raw=data,
        )

    def close(self) -> None:
        self._client.close()

