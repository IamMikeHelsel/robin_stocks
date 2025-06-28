#!/usr/bin/env python3
"""
Cryptocurrency Arbitrage Bot Example

This bot monitors price differences between Robinhood and Gemini
for cryptocurrency arbitrage opportunities.

⚠️  EDUCATIONAL PURPOSES ONLY ⚠️
Real arbitrage requires:
- Very fast execution
- Account for fees and slippage
- Handle transfer times between exchanges
- Comply with regulations

Usage:
    python crypto_arbitrage_bot.py
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

import robin_stocks.robinhood as rh
import robin_stocks.gemini as gem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crypto_arbitrage.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class CryptoArbitrageBot:
    """
    Monitor cryptocurrency prices across multiple exchanges for arbitrage opportunities.
    """

    def __init__(self):
        """Initialize the arbitrage bot."""
        self.dry_run = os.getenv("dry_run_mode", "true").lower() == "true"
        self.min_profit_threshold = 0.005  # 0.5% minimum profit
        self.api_delay = float(os.getenv("api_delay", "2.0"))

        # Crypto symbols to monitor (Gemini format)
        self.crypto_symbols = ["btcusd", "ethusd", "ltcusd"]

        # Symbol mapping between exchanges
        self.symbol_mapping = {
            "btcusd": "BTC",  # Gemini -> Robinhood
            "ethusd": "ETH",
            "ltcusd": "LTC",
        }

        logger.info(f"Crypto Arbitrage Bot initialized - Dry Run: {self.dry_run}")

    def authenticate(self) -> bool:
        """Authenticate with exchanges."""
        success_count = 0

        # Robinhood
        try:
            username = os.getenv("robin_username")
            password = os.getenv("robin_password")

            if username and password:
                rh.login(username, password)
                if rh.get_login_state():
                    logger.info("✓ Robinhood authentication successful")
                    success_count += 1
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
        except Exception as e:
            logger.error(f"Gemini authentication error: {e}")

        return success_count >= 2  # Need both exchanges

    def get_robinhood_crypto_price(self, symbol: str) -> Optional[float]:
        """
        Get cryptocurrency price from Robinhood.

        Args:
            symbol: Crypto symbol (e.g., 'BTC')

        Returns:
            float: Current price or None
        """
        try:
            if rh.get_login_state():
                price_data = rh.crypto.get_crypto_quote(symbol)
                if (
                    price_data
                    and "bid_price" in price_data
                    and "ask_price" in price_data
                ):
                    # Use mid price
                    bid = float(price_data["bid_price"])
                    ask = float(price_data["ask_price"])
                    return (bid + ask) / 2
        except Exception as e:
            logger.error(f"Error getting Robinhood price for {symbol}: {e}")

        return None

    def get_gemini_crypto_price(self, symbol: str) -> Optional[float]:
        """
        Get cryptocurrency price from Gemini.

        Args:
            symbol: Crypto symbol (e.g., 'btcusd')

        Returns:
            float: Current price or None
        """
        try:
            if gem.get_login_state():
                ticker = gem.get_pubticker(symbol)
                if ticker and "bid" in ticker and "ask" in ticker:
                    # Use mid price
                    bid = float(ticker["bid"])
                    ask = float(ticker["ask"])
                    return (bid + ask) / 2
        except Exception as e:
            logger.error(f"Error getting Gemini price for {symbol}: {e}")

        return None

    def calculate_arbitrage_opportunity(self, gemini_symbol: str) -> Dict:
        """
        Calculate arbitrage opportunity for a symbol.

        Args:
            gemini_symbol: Symbol in Gemini format

        Returns:
            dict: Arbitrage analysis
        """
        rh_symbol = self.symbol_mapping.get(gemini_symbol)
        if not rh_symbol:
            return {"error": "Symbol mapping not found"}

        # Get prices from both exchanges
        gemini_price = self.get_gemini_crypto_price(gemini_symbol)
        rh_price = self.get_robinhood_crypto_price(rh_symbol)

        if not gemini_price or not rh_price:
            return {"error": "Failed to get prices"}

        # Calculate arbitrage metrics
        price_diff = abs(gemini_price - rh_price)
        avg_price = (gemini_price + rh_price) / 2
        profit_percentage = price_diff / avg_price

        # Determine direction
        if gemini_price > rh_price:
            direction = "sell_gemini_buy_rh"
            profitable_exchange = "Gemini"
            cheaper_exchange = "Robinhood"
        else:
            direction = "sell_rh_buy_gemini"
            profitable_exchange = "Robinhood"
            cheaper_exchange = "Gemini"

        return {
            "symbol": gemini_symbol,
            "rh_symbol": rh_symbol,
            "gemini_price": gemini_price,
            "rh_price": rh_price,
            "price_diff": price_diff,
            "profit_percentage": profit_percentage,
            "direction": direction,
            "profitable_exchange": profitable_exchange,
            "cheaper_exchange": cheaper_exchange,
            "opportunity": profit_percentage >= self.min_profit_threshold,
        }

    def get_account_balances(self) -> Dict:
        """
        Get account balances from both exchanges.

        Returns:
            dict: Balance information
        """
        balances = {"robinhood": {}, "gemini": {}}

        # Robinhood balances
        try:
            if rh.get_login_state():
                crypto_positions = rh.crypto.get_crypto_positions()
                for position in crypto_positions:
                    if position and "currency" in position and "quantity" in position:
                        symbol = position["currency"]["code"]
                        quantity = float(position["quantity"])
                        if quantity > 0:
                            balances["robinhood"][symbol] = quantity
        except Exception as e:
            logger.error(f"Error getting Robinhood balances: {e}")

        # Gemini balances
        try:
            if gem.get_login_state():
                account_detail = gem.get_account_detail()
                if isinstance(account_detail, list):
                    for balance in account_detail:
                        if balance and "currency" in balance and "available" in balance:
                            symbol = balance["currency"]
                            available = float(balance["available"])
                            if available > 0:
                                balances["gemini"][symbol] = available
        except Exception as e:
            logger.error(f"Error getting Gemini balances: {e}")

        return balances

    def simulate_arbitrage_trade(
        self, opportunity: Dict, trade_amount_usd: float = 100.0
    ):
        """
        Simulate an arbitrage trade.

        Args:
            opportunity: Arbitrage opportunity data
            trade_amount_usd: Amount to trade in USD
        """
        symbol = opportunity["symbol"]
        profit_pct = opportunity["profit_percentage"]

        # Calculate trade details
        avg_price = (opportunity["gemini_price"] + opportunity["rh_price"]) / 2
        crypto_amount = trade_amount_usd / avg_price
        expected_profit = trade_amount_usd * profit_pct

        # Estimate fees (typical crypto trading fees)
        gemini_fee = trade_amount_usd * 0.0035  # 0.35% fee
        rh_fee = trade_amount_usd * 0.0025  # 0.25% fee (estimated)
        total_fees = gemini_fee + rh_fee

        net_profit = expected_profit - total_fees
        net_profit_pct = net_profit / trade_amount_usd

        logger.info(f"\n📊 ARBITRAGE SIMULATION - {symbol.upper()}")
        logger.info(f"   Gemini Price: ${opportunity['gemini_price']:.2f}")
        logger.info(f"   Robinhood Price: ${opportunity['rh_price']:.2f}")
        logger.info(
            f"   Price Difference: ${opportunity['price_diff']:.2f} ({profit_pct:.2%})"
        )
        logger.info(f"   Direction: {opportunity['direction']}")
        logger.info(f"   ")
        logger.info(f"   Trade Amount: ${trade_amount_usd:.2f}")
        logger.info(f"   Crypto Amount: {crypto_amount:.6f} {opportunity['rh_symbol']}")
        logger.info(f"   Gross Profit: ${expected_profit:.2f}")
        logger.info(f"   Estimated Fees: ${total_fees:.2f}")
        logger.info(f"   Net Profit: ${net_profit:.2f} ({net_profit_pct:.2%})")

        if net_profit > 0:
            logger.info(f"   ✅ Profitable after fees!")
        else:
            logger.info(f"   ❌ Not profitable after fees.")

    def monitor_arbitrage_opportunities(self):
        """
        Monitor and report arbitrage opportunities.
        """
        logger.info("🔍 Scanning for arbitrage opportunities...")

        opportunities = []

        for symbol in self.crypto_symbols:
            time.sleep(self.api_delay)  # Rate limiting

            opportunity = self.calculate_arbitrage_opportunity(symbol)

            if "error" in opportunity:
                logger.warning(f"❌ {symbol}: {opportunity['error']}")
                continue

            opportunities.append(opportunity)

            # Log opportunity
            if opportunity["opportunity"]:
                logger.info(
                    f"🚨 OPPORTUNITY: {symbol} - {opportunity['profit_percentage']:.2%} profit"
                )
                self.simulate_arbitrage_trade(opportunity)
            else:
                logger.info(
                    f"📈 {symbol}: {opportunity['profit_percentage']:.3%} (below threshold)"
                )

        return opportunities

    def run_monitoring_cycle(self, duration_minutes: int = 60):
        """
        Run continuous monitoring for specified duration.

        Args:
            duration_minutes: How long to monitor
        """
        logger.info(f"Starting {duration_minutes} minute monitoring cycle...")

        start_time = time.time()
        cycle_count = 0

        while (time.time() - start_time) < (duration_minutes * 60):
            cycle_count += 1
            logger.info(f"\n=== Monitoring Cycle {cycle_count} ===")

            try:
                opportunities = self.monitor_arbitrage_opportunities()

                # Summary
                profitable_ops = [
                    op for op in opportunities if op.get("opportunity", False)
                ]
                logger.info(
                    f"\n📋 Cycle Summary: {len(profitable_ops)}/{len(opportunities)} profitable opportunities"
                )

                # Wait before next cycle
                logger.info("⏱️  Waiting for next scan...")
                time.sleep(30)  # 30 seconds between scans

            except KeyboardInterrupt:
                logger.info("\n👋 Monitoring stopped by user.")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(10)  # Wait before retrying

        logger.info(f"\n🏁 Monitoring completed. Total cycles: {cycle_count}")

    def run(self):
        """
        Run the arbitrage monitoring bot.
        """
        logger.info("🤖 Crypto Arbitrage Bot Starting...")

        # Authenticate
        if not self.authenticate():
            logger.error(
                "❌ Authentication failed. Need both Robinhood and Gemini access."
            )
            return

        # Show account balances
        logger.info("\n💰 Account Balances:")
        balances = self.get_account_balances()

        for exchange, exchange_balances in balances.items():
            logger.info(f"   {exchange.title()}:")
            if exchange_balances:
                for symbol, amount in exchange_balances.items():
                    logger.info(f"     {symbol}: {amount:.6f}")
            else:
                logger.info(f"     No crypto positions found")

        # Run monitoring
        try:
            self.run_monitoring_cycle(duration_minutes=60)
        except Exception as e:
            logger.error(f"Error running bot: {e}")

        logger.info("\n👋 Arbitrage bot finished.")


def main():
    """
    Main function to run the crypto arbitrage bot.
    """
    print("💰 Crypto Arbitrage Monitor")
    print("===========================")
    print("⚠️  This is for educational purposes only!")
    print("   Real arbitrage requires fast execution,")
    print("   account for fees, and handle risks.\n")

    # Check configuration
    if not os.path.exists(".env"):
        print("❌ No .env file found!")
        print("Please configure your credentials first.")
        return

    # Create and run bot
    bot = CryptoArbitrageBot()
    bot.run()


if __name__ == "__main__":
    main()
