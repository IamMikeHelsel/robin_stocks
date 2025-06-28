# Robin Stocks Trading Bot Setup Guide

This guide will help you set up and configure the Robin Stocks library for algorithmic trading and investment strategies.

## Prerequisites

- Python 3.9 or higher
- Active accounts with one or more supported brokers:
  - Robinhood (stocks, options, crypto)
  - TD Ameritrade (stocks, options) 
  - Gemini (cryptocurrency)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/jmfernandes/robin_stocks.git
cd robin_stocks

# Install in development mode
pip install -e .

# Install additional testing dependencies
pip install pytest pytest-dotenv
```

### 2. Configuration

```bash
# Copy the environment template
cp .env.template .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

### 3. API Credentials Setup

#### Robinhood Setup
1. Use your existing Robinhood login credentials
2. Enable 2FA in your Robinhood app
3. Add your username/password to `.env`

#### Gemini Setup
1. Go to [Gemini API Settings](https://exchange.gemini.com/settings/api)
2. Create a new API key with trading permissions
3. Add the key and secret to `.env`
4. For testing, use sandbox mode (`gemini_sandbox=true`)

#### TD Ameritrade Setup
1. Visit [TD Ameritrade Developer Portal](https://developer.tdameritrade.com/)
2. Create a developer account and application
3. Get your Consumer Key (Client ID)
4. Complete OAuth flow to get initial tokens
5. Use the provided encryption passcode in `.env`

## Detailed Setup Instructions

### Environment Configuration

The `.env` file contains all configuration options. Key sections:

**Trading Safety:**
```bash
# Enable paper trading mode for testing
dry_run_mode=true

# Risk management
max_position_size=0.05  # 5% max per position
daily_loss_limit=0.02   # 2% daily loss limit
```

**API Rate Limiting:**
```bash
api_delay=1.0      # 1 second between calls
max_retries=3      # Retry failed calls
```

### Authentication Flow

#### First-Time Robinhood Login
```python
import robin_stocks.robinhood as rh

# Login with 2FA
login = rh.login('username', 'password', mfa_code='123456')

# Session will be saved for future use
```

#### First-Time TD Ameritrade Setup
```python
import robin_stocks.tda as tda

# First time setup (requires manual OAuth)
tda.login_first_time(
    encryption_passcode='your_passcode',
    client_id='your_client_id', 
    authorization_token='oauth_token',
    refresh_token='refresh_token'
)

# Subsequent logins
tda.login('your_passcode')
```

#### Gemini Setup
```python
import robin_stocks.gemini as gem

# Login with API keys
gem.login('api_key', 'secret_key', sandbox=True)
```

## Testing Your Setup

### Run Unit Tests (No Credentials Required)
```bash
# Test mocked functions
pytest tests/test_unit_mocks.py -v

# Test trading bot logic
pytest tests/test_trading_bot.py -v
```

### Run Integration Tests (Requires Credentials)
```bash
# Test all APIs with real credentials
pytest tests/ -v

# Test specific API
pytest tests/test_robinhood.py -v
pytest tests/test_gemini.py -v
pytest tests/test_tda.py -v

# Test specific functionality
pytest tests/test_robinhood.py -k "test_login" -v
```

### Verify API Connections
```python
# Quick connection test
python3 -c "
import robin_stocks.robinhood as rh
import robin_stocks.gemini as gem
import robin_stocks.tda as tda
import os
from dotenv import load_dotenv

load_dotenv()

# Test Robinhood
print('Testing Robinhood...')
rh.login(os.getenv('robin_username'), os.getenv('robin_password'))
print(f'Robinhood logged in: {rh.get_login_state()}')

# Test Gemini  
print('Testing Gemini...')
gem.login(os.getenv('gemini_account_key'), os.getenv('gemini_account_secret'))
print(f'Gemini logged in: {gem.get_login_state()}')

# Test TDA
print('Testing TD Ameritrade...')
tda.login(os.getenv('tda_encryption_passcode'))
print(f'TDA logged in: {tda.get_login_state()}')

print('All APIs connected successfully!')
"
```

## Trading Bot Development

### Basic Trading Bot Structure
```python
import robin_stocks.robinhood as rh
from dotenv import load_dotenv
import os
import time

load_dotenv()

class TradingBot:
    def __init__(self):
        self.dry_run = os.getenv('dry_run_mode', 'true').lower() == 'true'
        self.max_position_size = float(os.getenv('max_position_size', '0.05'))
        
    def login(self):
        """Authenticate with all APIs"""
        rh.login(os.getenv('robin_username'), os.getenv('robin_password'))
        
    def get_portfolio_value(self):
        """Get current portfolio value"""
        portfolio = rh.get_portfolio()
        return float(portfolio['market_value'])
        
    def calculate_position_size(self, symbol, price):
        """Calculate position size based on risk management"""
        portfolio_value = self.get_portfolio_value()
        max_value = portfolio_value * self.max_position_size
        shares = int(max_value / price)
        return max(1, shares)
        
    def place_order(self, symbol, side='buy', quantity=1):
        """Place order with dry run support"""
        if self.dry_run:
            print(f"DRY RUN: {side} {quantity} shares of {symbol}")
            return {'status': 'dry_run'}
        else:
            if side == 'buy':
                return rh.orders.order_buy_market(symbol, quantity)
            else:
                return rh.orders.order_sell_market(symbol, quantity)

# Usage
bot = TradingBot()
bot.login()
bot.place_order('AAPL', 'buy', 10)
```

## Security Best Practices

### Credential Protection
- **Never commit `.env` file** to version control
- Use strong encryption passcodes for TDA
- Enable 2FA on all broker accounts
- Rotate API keys regularly

### Trading Safety
- **Always start with `dry_run_mode=true`**
- Use small position sizes initially
- Set stop losses and daily limits
- Monitor all trades closely

### Data Protection
- Session files are stored in `~/.tokens/`
- TDA credentials are encrypted with Fernet
- Robinhood uses device tokens for security

## Troubleshooting

### Common Issues

**Authentication Failures:**
```bash
# Clear cached sessions
rm -rf ~/.tokens/

# Check credentials in .env
cat .env | grep -E "(username|password|key|secret)"
```

**API Rate Limiting:**
```python
# Add delays between calls
import time
time.sleep(1)  # 1 second delay
```

**2FA Issues:**
```python
# Use TOTP for reliable 2FA
import pyotp
totp = pyotp.TOTP('your_secret_key')
mfa_code = totp.now()
```

### Testing Connectivity
```bash
# Test network connectivity
curl -I https://api.robinhood.com/
curl -I https://api.gemini.com/
curl -I https://api.tdameritrade.com/

# Check Python dependencies
pip check
```

### Getting Help

1. **Check the documentation:** [robin-stocks.com](http://www.robin-stocks.com/)
2. **Join the Slack channel:** [Robin Stocks Community](https://join.slack.com/t/robin-stocks/shared_invite/zt-7up2htza-wNSil5YDa3zrAglFFSxRIA)
3. **Search GitHub issues:** [GitHub Issues](https://github.com/jmfernandes/robin_stocks/issues)

## Next Steps

1. **Start with paper trading** (`dry_run_mode=true`)
2. **Implement basic strategies** (moving averages, RSI)
3. **Add risk management** (stop losses, position sizing)
4. **Backtest strategies** using historical data
5. **Monitor and iterate** on performance

## Legal Disclaimer

- This software is for educational purposes
- Trading involves substantial risk
- Past performance doesn't guarantee future results
- Comply with all applicable laws and regulations
- The authors are not responsible for trading losses

## Contributing

See [contributing.md](contributing.md) for development guidelines.