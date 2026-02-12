## Binance Futures Testnet Trading Bot (Python)

Simple CLI trading bot that places MARKET, LIMIT, and STOP_LIMIT orders on **Binance Futures Testnet (USDT-M)** using direct REST calls.

### Features

- **Market, Limit, and Stop-Limit orders** on Binance Futures Testnet (USDT-M)
- **BUY / SELL** support
- **CLI** built with Typer
- **Structured code** with clear client, order, and validation layers
- **Logging** of requests, responses, and errors to rotating log files
- **Environment-based credentials** with `.env` support

### Requirements

- Python 3.10+
- Binance Futures **Testnet** account and API keys
- Network access to `https://testnet.binancefuture.com`

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Mukul2425/Binance-Futures-Bot.git
   cd Binance-Futures-Bot
   ```

2. **Create and activate a virtual environment (recommended)**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**

   - Copy `.env.example` to `.env`:

     ```bash
     cp .env.example .env
     ```

   - Edit `.env` and set your Binance Futures **Testnet** credentials:

     ```bash
     BINANCE_API_KEY=your_testnet_api_key_here
     BINANCE_API_SECRET=your_testnet_api_secret_here
     ```

   Alternatively, export `BINANCE_API_KEY` and `BINANCE_API_SECRET` directly in your shell.

### Usage

The CLI entry point is `cli.py`. Help:

```bash
python cli.py --help
```

#### Place a MARKET order

```bash
python cli.py order BTCUSDT BUY MARKET 0.001 --log-file market_order.log
```

#### Place a LIMIT order

```bash
python cli.py order BTCUSDT SELL LIMIT 0.001 --price 90000 --log-file limit_order.log
```

#### Place a STOP_LIMIT order

```bash
python cli.py order BTCUSDT BUY STOP_LIMIT 0.001 --price 85000 --stop-price 84000 --log-file stop_limit_order.log
```

Arguments:

- `symbol` (positional): trading pair, e.g. `BTCUSDT`
- `side` (positional): `BUY` or `SELL`
- `order_type` (positional): `MARKET`, `LIMIT`, or `STOP_LIMIT`
- `quantity` (positional): order quantity (float)
- `--price` / `-p`: required for `LIMIT` and `STOP_LIMIT` orders
- `--stop-price`: required for `STOP_LIMIT` orders
- `--log-file` / `-l`: optional log file name inside `logs/` (default: `trading_bot.log`)

On each run, the bot will:

- Validate input (symbol, side, order type, quantity, price, stop price)
- Print an **order request summary**
- Call Binance Futures Testnet `/fapi/v1/order`
- Print an **order response table**:
  - `orderId`
  - `status`
  - `executedQty`
  - `avgPrice` (if available)
- Print a success or failure message

### Logging

- Logs are written to the `logs/` directory (created automatically).
- Default log file: `logs/trading_bot.log`
- If you pass `--log-file market_order.log`, logs go to `logs/market_order.log`
- Logged information includes:
  - Outgoing requests (method, URL, query parameters – without secrets)
  - Binance responses (status code, body)
  - Order placement summaries and results
  - Exceptions and error messages

For the assignment, you can:

- Run **one MARKET** and **one LIMIT** order as shown above.
- Attach the resulting log files (e.g. `logs/market_order.log`, `logs/limit_order.log`) to your email.

### Project Structure

```text
bot/
  __init__.py
  client.py         # Binance Futures REST client (testnet)
  orders.py         # Order placement logic with logging
  validators.py     # Input validation and normalization
  logging_config.py # Central logging configuration
cli.py              # Typer-based CLI entry point
requirements.txt
README.md
.env.example
```

### Assumptions

- Only **USDT-M Futures** on **Binance Testnet** are supported.
- **MARKET**, **LIMIT**, and **STOP_LIMIT** order types are implemented (STOP_LIMIT via Binance `type=STOP`).
- Position mode, leverage, margin, and other advanced order types are out of scope for this exercise.

