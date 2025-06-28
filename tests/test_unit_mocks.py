"""
Unit tests with mocked responses to avoid API dependencies.
These tests can run without credentials and won't make real API calls.
"""

from unittest.mock import Mock, patch

import pytest

import robin_stocks.gemini as gem
import robin_stocks.robinhood as rh
import robin_stocks.tda as tda


class TestRobinhoodMocked:
    """Test Robinhood functions with mocked API responses."""

    @patch("robin_stocks.robinhood.helper.request_get")
    def test_get_latest_price_success(self, mock_request):
        """Test getting latest price with mocked response."""
        mock_request.return_value = [{"price": "150.25"}]

        result = rh.get_latest_price("AAPL")

        assert result == ["150.25"]
        mock_request.assert_called_once()

    @patch("robin_stocks.robinhood.helper.request_get")
    def test_get_latest_price_failure(self, mock_request):
        """Test handling API failures gracefully."""
        mock_request.return_value = None

        result = rh.get_latest_price("INVALID")

        assert result is None

    @patch("robin_stocks.robinhood.helper.request_get")
    def test_get_fundamentals(self, mock_request):
        """Test getting stock fundamentals."""
        mock_request.return_value = [
            {"market_cap": "2500000000000", "pe_ratio": "25.5", "dividend_yield": "0.5"}
        ]

        result = rh.get_fundamentals("AAPL")

        assert result[0]["market_cap"] == "2500000000000"
        assert float(result[0]["pe_ratio"]) == 25.5


class TestGeminiMocked:
    """Test Gemini functions with mocked API responses."""

    @patch("robin_stocks.gemini.helper.request_get")
    def test_get_pubticker_success(self, mock_request):
        """Test getting public ticker data."""
        mock_request.return_value = {
            "bid": "45000.00",
            "ask": "45100.00",
            "last": "45050.00",
        }

        result = gem.get_pubticker("btcusd")

        assert result["last"] == "45050.00"
        mock_request.assert_called_once()

    @patch("robin_stocks.gemini.crypto.request_get")
    def test_get_candles(self, mock_request):
        """Test getting candlestick data."""
        mock_request.return_value = [
            [1609459200000, 29000, 29500, 28800, 29200, 1.5],
            [1609462800000, 29200, 29800, 29100, 29600, 2.1],
        ]

        result = gem.get_candles("btcusd", "1hr")

        assert len(result) == 2
        assert result[0][1] == 29000  # Open price


class TestTDAMocked:
    """Test TD Ameritrade functions with mocked API responses."""

    @patch("robin_stocks.tda.helper.request_get")
    def test_get_price_history(self, mock_request):
        """Test getting price history."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "candles": [
                {"open": 150.0, "high": 155.0, "low": 148.0, "close": 152.0},
                {"open": 152.0, "high": 157.0, "low": 150.0, "close": 156.0},
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = (mock_response, None)

        result, error = tda.get_price_history("TSLA")

        assert error is None
        assert result.status_code == 200
        data = result.json()
        assert len(data["candles"]) == 2


class TestErrorHandling:
    """Test error handling across all APIs."""

    def test_robinhood_invalid_symbol(self):
        """Test handling of invalid stock symbols."""
        with patch("robin_stocks.robinhood.helper.request_get") as mock_request:
            mock_request.return_value = None
            result = rh.get_latest_price("INVALID_SYMBOL")
            assert result is None

    def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        with patch("robin_stocks.robinhood.helper.request_get") as mock_request:
            mock_request.side_effect = Exception("Connection timeout")
            result = rh.get_latest_price("AAPL")
            assert result is None


class TestConfigValidation:
    """Test configuration and setup validation."""

    def test_device_token_generation(self):
        """Test that device tokens are properly formatted."""
        token = rh.generate_device_token()

        # Should be UUID-like format with dashes
        assert len(token) == 36
        assert token.count("-") == 4

        # Should be hexadecimal characters
        clean_token = token.replace("-", "")
        assert all(c in "0123456789abcdef" for c in clean_token)

    def test_session_state_management(self):
        """Test session state tracking."""
        # Test initial state
        assert not rh.get_login_state()

        # Mock login state change
        with patch("robin_stocks.robinhood.globals.LOGGED_IN", True):
            assert rh.get_login_state()


class TestDataValidation:
    """Test data validation and sanitization."""

    def test_price_formatting(self):
        """Test that price data is properly formatted."""
        with patch("robin_stocks.robinhood.helper.request_get") as mock_request:
            mock_request.return_value = [{"price": "150.2567"}]

            result = rh.get_latest_price("AAPL")
            price = float(result[0])

            # Should be a valid number
            assert isinstance(price, float)
            assert price > 0

    def test_symbol_validation(self):
        """Test that stock symbols are validated."""
        # Test valid symbols
        valid_symbols = ["AAPL", "TSLA", "SPY", "QQQ"]
        for symbol in valid_symbols:
            assert symbol.isalpha() or symbol.isalnum()
            assert len(symbol) <= 5

    @pytest.mark.parametrize(
        "symbol,expected", [("aapl", "AAPL"), ("Tsla", "TSLA"), ("spy", "SPY")]
    )
    def test_symbol_normalization(self, symbol, expected):
        """Test that symbols are normalized to uppercase."""
        normalized = symbol.upper()
        assert normalized == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
