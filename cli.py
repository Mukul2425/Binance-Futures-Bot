from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from dotenv import load_dotenv
from rich import print as rprint
from rich.table import Table

from bot.client import BinanceApiError, BinanceFuturesClient, BinanceNetworkError
from bot.logging_config import configure_logging
from bot.orders import place_order_with_validation
from bot.validators import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Simple Binance Futures Testnet trading bot CLI."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    order_parser = subparsers.add_parser(
        "order", help="Place an order on Binance Futures Testnet (USDT-M)."
    )
    order_parser.add_argument("symbol", help="Trading pair symbol, e.g. BTCUSDT.")
    order_parser.add_argument("side", help="Order side: BUY or SELL.")
    order_parser.add_argument(
        "order_type",
        help="Order type: MARKET, LIMIT, or STOP_LIMIT.",
    )
    order_parser.add_argument(
        "quantity",
        type=float,
        help="Order quantity.",
    )
    order_parser.add_argument(
        "--price",
        "-p",
        type=float,
        required=False,
        help="Price (required for LIMIT and STOP_LIMIT orders).",
    )
    order_parser.add_argument(
        "--stop-price",
        type=float,
        required=False,
        help="Trigger price for STOP_LIMIT orders.",
    )
    order_parser.add_argument(
        "--log-file",
        "-l",
        required=False,
        help="Optional log file name inside logs/ (default: trading_bot.log).",
    )

    return parser


def handle_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
    stop_price: Optional[float],
    log_file: Optional[str],
) -> int:
    """
    Place a MARKET, LIMIT, or STOP_LIMIT order on Binance Futures Testnet (USDT-M).
    Returns process exit code.
    """
    # Load environment variables from .env if present
    load_dotenv()

    configure_logging(log_file=log_file)

    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        rprint(
            "[bold red]BINANCE_API_KEY and BINANCE_API_SECRET must be set "
            "(e.g. in a .env file or environment).[/bold red]"
        )
        return 1

    rprint("[bold cyan]Order request summary[/bold cyan]")
    rprint(
        f"Symbol: [bold]{symbol}[/bold], Side: [bold]{side}[/bold], "
        f"Type: [bold]{order_type}[/bold], Qty: [bold]{quantity}[/bold], "
        f"Price: [bold]{price}[/bold], StopPrice: [bold]{stop_price}[/bold]"
    )

    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    try:
        result = place_order_with_validation(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValidationError as exc:
        rprint(f"[bold red]Validation error:[/bold red] {exc}")
        return 1
    except BinanceApiError as exc:
        rprint(f"[bold red]Binance API error:[/bold red] {exc}")
        return 1
    except BinanceNetworkError as exc:
        rprint(f"[bold red]Network error while calling Binance:[/bold red] {exc}")
        return 1
    finally:
        client.close()

    table = Table(title="Order Response")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("orderId", str(result.order_id))
    table.add_row("status", result.status)
    table.add_row("executedQty", result.executed_qty)
    table.add_row("avgPrice", result.avg_price or "-")

    rprint(table)
    rprint("[bold green]Order placed successfully on Binance Futures Testnet.[/bold green]")
    return 0


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "order":
        exit_code = handle_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            log_file=args.log_file,
        )
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
