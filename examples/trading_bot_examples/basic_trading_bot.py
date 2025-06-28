#!/usr/bin/env python3
"""
Basic Trading Bot Example

This example demonstrates a simple trading bot that:
1. Connects to multiple APIs
2. Implements basic risk management
3. Uses moving average crossover strategy
4. Supports dry run mode for testing

Usage:
    python basic_trading_bot.py

Make sure to configure your .env file first!
"""

import logging
import os
import time
from typing import Optional

from dotenv import load_dotenv

import robin_stocks.gemini as gem
import robin_stocks.robinhood as rh
import robin_stocks.tda as tda

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("log_level", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("log_file", "trading_bot.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class BasicTradingBot:
    """
    A basic trading bot with risk management and multi-API support.
    """

    def __init__(self):
        """Initialize the trading bot with configuration from environment."""
        self.dry_run = os.getenv("dry_run_mode", "true").lower() == "true"
        self.max_position_size = float(os.getenv("max_position_size", "0.05"))
        self.daily_loss_limit = float(os.getenv("daily_loss_limit", "0.02"))
        self.default_stop_loss = float(os.getenv("default_stop_loss", "0.02"))
        self.default_take_profit = float(os.getenv("default_take_profit", "0.05"))
        self.api_delay = float(os.getenv("api_delay", "1.0"))

        # Trading symbols
        self.stock_symbols = os.getenv("stock_symbols", "AAPL,TSLA,SPY").split(",")
        self.crypto_symbols = os.getenv("crypto_symbols", "btcusd,ethusd").split(",")

        # Strategy parameters
        self.short_ma_period = int(os.getenv("short_ma_period", "10"))
        self.long_ma_period = int(os.getenv("long_ma_period", "20"))

        # Track daily performance
        self.starting_balance = 0.0
        self.current_balance = 0.0
        self.daily_pnl = 0.0

        logger.info(f"Trading Bot initialized - Dry Run: {self.dry_run}")

    def authenticate(self) -> bool:
        """
        Authenticate with all configured APIs.

        Returns:
            bool: True if at least one API connection successful
        """
        success_count = 0

        # Robinhood
        try:
            username = os.getenv("robin_username")
            password = os.getenv("robin_password")
            mfa_code = os.getenv("robin_mfa")

            if username and password:
                rh.login(username, password, mfa_code=mfa_code)
                if rh.get_login_state():
                    logger.info("✓ Robinhood authentication successful")
                    success_count += 1
                else:
                    logger.warning("✗ Robinhood authentication failed")
        except Exception as e:
            logger.error(f"Robinhood authentication error: {e}")

        # Gemini
        try:
            api_key = os.getenv("gemini_account_key")
            secret_key = os.getenv("gemini_account_secret")
            sandbox = os.getenv("gemini_sandbox", "true").lower() == "true"

            if api_key and secret_key:
                gem.login(api_key, secret_key, sandbox=sandbox)
                if gem.get_login_state():
                    logger.info("✓ Gemini authentication successful")
                    success_count += 1
                else:
                    logger.warning("✗ Gemini authentication failed")
        except Exception as e:
            logger.error(f"Gemini authentication error: {e}")

        # TD Ameritrade
        try:
            encryption_passcode = os.getenv("tda_encryption_passcode")

            if encryption_passcode:
                tda.login(encryption_passcode)
                if tda.get_login_state():
                    logger.info("✓ TD Ameritrade authentication successful")
                    success_count += 1
                else:
                    logger.warning("✗ TD Ameritrade authentication failed")
        except Exception as e:
            logger.error(f"TD Ameritrade authentication error: {e}")

        return success_count > 0

    def get_portfolio_value(self) -> float:
        """
        Get current portfolio value from Robinhood.

        Returns:
            float: Portfolio value in USD
        """
        try:
            if rh.get_login_state():
                portfolio = rh.get_portfolio()
                if portfolio and "market_value" in portfolio:
                    return float(portfolio["market_value"])
        except Exception as e:
            logger.error(f"Error getting portfolio value: {e}")

        return 0.0

    def check_daily_loss_limit(self) -> bool:
        """
        Check if daily loss limit has been reached.

        Returns:
            bool: True if trading should stop due to loss limit
        """
        if self.starting_balance == 0:
            return False

        self.current_balance = self.get_portfolio_value()
        self.daily_pnl = (
            self.current_balance - self.starting_balance
        ) / self.starting_balance

        if self.daily_pnl <= -self.daily_loss_limit:
            logger.warning(f"Daily loss limit reached: {self.daily_pnl:.2%}")
            return True

        return False

    def calculate_position_size(self, symbol: str, price: float) -> int:
        """
        Calculate position size based on risk management rules.

        Args:
            symbol: Stock symbol
            price: Current price per share

        Returns:
            int: Number of shares to trade
        """
        portfolio_value = self.get_portfolio_value()
        if portfolio_value == 0:
            return 0

        max_value = portfolio_value * self.max_position_size
        shares = int(max_value / price)

        return max(1, shares)

    def get_moving_averages(self, symbol: str) -> dict[str, Optional[float]]:
        """
        Calculate moving averages for a symbol.

        Args:
            symbol: Stock symbol

        Returns:
            dict: Short and long moving averages
        """
        try:
            # Get historical data (simplified - in production use proper historical data)
            if rh.get_login_state():
                historicals = rh.get_stock_historicals(
                    symbol, interval="day", span="month"
                )

                if historicals and len(historicals) >= self.long_ma_period:
                    prices = [
                        float(h["close_price"])
                        for h in historicals[-self.long_ma_period :]
                    ]

                    short_ma = (
                        sum(prices[-self.short_ma_period :]) / self.short_ma_period
                    )
                    long_ma = sum(prices) / self.long_ma_period

                    return {
                        "short_ma": short_ma,
                        "long_ma": long_ma,
                        "current_price": prices[-1],
                    }
        except Exception as e:
            logger.error(f"Error calculating moving averages for {symbol}: {e}")

        return {"short_ma": None, "long_ma": None, "current_price": None}

    def should_buy(self, symbol: str) -> bool:
        """
        Determine if we should buy a symbol based on strategy.

        Args:
            symbol: Stock symbol

        Returns:
            bool: True if should buy
        """
        mas = self.get_moving_averages(symbol)

        # Buy signal: short MA crosses above long MA
        if all(mas.values()) and mas["short_ma"] > mas["long_ma"]:
            logger.info(
                f"{symbol}: Buy signal - Short MA {mas['short_ma']:.2f} > Long MA {mas['long_ma']:.2f}"
            )
            return True

        return False

    def should_sell(self, symbol: str) -> bool:
        """
        Determine if we should sell a symbol based on strategy.

        Args:
            symbol: Stock symbol

        Returns:
            bool: True if should sell
        """
        mas = self.get_moving_averages(symbol)

        # Sell signal: short MA crosses below long MA
        if all(mas.values()) and mas["short_ma"] < mas["long_ma"]:
            logger.info(
                f"{symbol}: Sell signal - Short MA {mas['short_ma']:.2f} < Long MA {mas['long_ma']:.2f}"
            )
            return True

        return False

    def place_buy_order(self, symbol: str, quantity: int) -> Optional[dict]:
        """
        Place a buy order.

        Args:
            symbol: Stock symbol
            quantity: Number of shares

        Returns:
            dict: Order result or None
        """
        if self.dry_run:
            logger.info(f"DRY RUN: BUY {quantity} shares of {symbol}")
            return {"status": "dry_run_buy", "symbol": symbol, "quantity": quantity}

        try:
            if rh.get_login_state():
                order = rh.orders.order_buy_market(symbol, quantity)
                logger.info(f"BUY order placed: {quantity} shares of {symbol}")
                return order
        except Exception as e:
            logger.error(f"Error placing buy order for {symbol}: {e}")

        return None

    def place_sell_order(self, symbol: str, quantity: int) -> Optional[dict]:
        """
        Place a sell order.

        Args:
            symbol: Stock symbol
            quantity: Number of shares

        Returns:
            dict: Order result or None
        """
        if self.dry_run:
            logger.info(f"DRY RUN: SELL {quantity} shares of {symbol}")
            return {"status": "dry_run_sell", "symbol": symbol, "quantity": quantity}

        try:
            if rh.get_login_state():
                order = rh.orders.order_sell_market(symbol, quantity)
                logger.info(f"SELL order placed: {quantity} shares of {symbol}")
                return order
        except Exception as e:
            logger.error(f"Error placing sell order for {symbol}: {e}")

        return None

    def get_current_positions(self) -> dict[str, int]:
        """
        Get current stock positions.

        Returns:
            dict: Symbol -> quantity mapping
        """
        positions = {}

        try:
            if rh.get_login_state():
                holdings = rh.get_open_stock_positions()
                for holding in holdings:
                    if holding and "quantity" in holding and "symbol" in holding:
                        quantity = int(float(holding["quantity"]))
                        if quantity > 0:
                            positions[holding["symbol"]] = quantity
        except Exception as e:
            logger.error(f"Error getting positions: {e}")

        return positions

    def run_trading_cycle(self):
        """Run one trading cycle for all symbols."""
        logger.info("Starting trading cycle...")

        # Check daily loss limit
        if self.check_daily_loss_limit():
            logger.warning("Daily loss limit reached. Stopping trading.")
            return

        # Get current positions
        positions = self.get_current_positions()

        # Process each symbol
        for symbol in self.stock_symbols:
            try:
                time.sleep(self.api_delay)  # Rate limiting

                # Get current price
                price_data = rh.get_latest_price(symbol)
                if not price_data:
                    continue

                current_price = float(price_data[0])
                current_quantity = positions.get(symbol, 0)

                logger.info(
                    f"{symbol}: Price ${current_price:.2f}, Holdings: {current_quantity}"
                )

                # Trading logic
                if current_quantity == 0:
                    # No position - check for buy signal
                    if self.should_buy(symbol):
                        quantity = self.calculate_position_size(symbol, current_price)
                        if quantity > 0:
                            self.place_buy_order(symbol, quantity)

                else:
                    # Have position - check for sell signal
                    if self.should_sell(symbol):
                        self.place_sell_order(symbol, current_quantity)

            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")

        # Log performance
        if self.starting_balance > 0:
            logger.info(
                f"Daily P&L: {self.daily_pnl:.2%} (${self.current_balance - self.starting_balance:.2f})"
            )

    def run(self, cycles: int = 1):
        """
        Run the trading bot.

        Args:
            cycles: Number of trading cycles to run
        """
        logger.info("Starting Trading Bot...")

        # Authenticate
        if not self.authenticate():
            logger.error("Authentication failed for all APIs. Exiting.")
            return

        # Set starting balance
        self.starting_balance = self.get_portfolio_value()
        logger.info(f"Starting portfolio value: ${self.starting_balance:.2f}")

        # Run trading cycles
        for cycle in range(cycles):
            logger.info(f"=== Trading Cycle {cycle + 1}/{cycles} ===")

            try:
                self.run_trading_cycle()

                if cycle < cycles - 1:
                    logger.info("Waiting for next cycle...")
                    time.sleep(60)  # Wait 1 minute between cycles

            except KeyboardInterrupt:
                logger.info("Trading bot stopped by user.")
                break
            except Exception as e:
                logger.error(f"Error in trading cycle: {e}")

        logger.info("Trading bot finished.")


def main():
    """Main function to run the trading bot."""
    print("🤖 Basic Trading Bot")
    print("===================")

    # Check if configuration exists
    if not os.path.exists(".env"):
        print("❌ No .env file found!")
        print("Please copy .env.template to .env and configure your credentials.")
        return

    # Create and run bot
    bot = BasicTradingBot()

    # Run for 5 cycles (adjust as needed)
    bot.run(cycles=5)


if __name__ == "__main__":
    main()
