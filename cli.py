from __future__ import annotations

import os
from typing import Optional

import typer
from dotenv import load_dotenv
from rich import print as rprint
from rich.table import Table

from bot.client import BinanceApiError, BinanceFuturesClient, BinanceNetworkError
from bot.logging_config import configure_logging
from bot.orders import place_order_with_validation
from bot.validators import ValidationError

app = typer.Typer(help="Simple Binance Futures Testnet trading bot CLI.")


@app.command("order")
def place_order(
    symbol: str = typer.Argument(..., help="Trading pair symbol, e.g. BTCUSDT."),
    side: str = typer.Argument(..., help="Order side: BUY or SELL."),
    order_type: str = typer.Argument(..., help="Order type: MARKET or LIMIT."),
    quantity: float = typer.Argument(..., help="Order quantity."),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        "-p",
        help="Price (required for LIMIT orders).",
    ),
    log_file: Optional[str] = typer.Option(
        None,
        "--log-file",
        "-l",
        help="Optional log file name inside logs/ (default: trading_bot.log).",
    ),
) -> None:
    """
    Place a MARKET or LIMIT order on Binance Futures Testnet (USDT-M).
    """
    # Load environment variables from .env if present
    load_dotenv()

    configure_logging(log_file=log_file)

    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        typer.secho(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set "
            "(e.g. in a .env file or environment).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    rprint("[bold cyan]Order request summary[/bold cyan]")
    rprint(
        f"Symbol: [bold]{symbol}[/bold], Side: [bold]{side}[/bold], "
        f"Type: [bold]{order_type}[/bold], Qty: [bold]{quantity}[/bold], "
        f"Price: [bold]{price}[/bold]"
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
        )
    except ValidationError as exc:
        typer.secho(f"Validation error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except BinanceApiError as exc:
        typer.secho(f"Binance API error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except BinanceNetworkError as exc:
        typer.secho(f"Network error while calling Binance: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
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


def main() -> None:
    app()


if __name__ == "__main__":
    main()

