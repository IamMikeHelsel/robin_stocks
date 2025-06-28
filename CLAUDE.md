# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Robin Stocks is a Python library providing unified access to three financial APIs: Robinhood, Gemini, and TD Ameritrade. It enables real-time market data access, algorithmic trading, and investment portfolio management for stocks, options, and cryptocurrencies.

## Architecture

### Three-API Module Structure
The codebase is organized as three parallel API modules in `robin_stocks/`:

- **robinhood/**: Most comprehensive module (stocks, options, crypto, account management)
- **gemini/**: Cryptocurrency-focused API with simpler structure  
- **tda/**: Traditional brokerage API for stocks and market data

Each module follows identical patterns:
- `authentication.py`: Login/logout and session management
- `globals.py`: Session objects, headers, and global state
- `helper.py`: Request utilities and decorators with @login_required
- `urls.py`: API endpoint definitions
- `orders.py`: Trading functionality
- Module-specific files for stocks, crypto, accounts, etc.

### Authentication Patterns

**Robinhood**: Complex 2FA/MFA flow with device tokens, session persistence via pickle files in `~/.tokens/robinhood.pickle`, Sheriff verification system for email/SMS/app verification

**TD Ameritrade**: Encrypted credential storage using Fernet encryption, automatic token refresh (30-min auth tokens, 60-day refresh tokens), stores encrypted credentials in `~/.tokens/tda.pickle`

**Gemini**: API key-based authentication with HMAC-SHA384 signatures, nonce-based request ordering, sandbox environment support

### Session Management
All APIs use global SESSION objects (requests.Session) with login state tracking via LOGGED_IN flags and @login_required decorators for protected functions.

## Development Commands

```bash
# Install for development
pip install .

# Install dependencies  
pip install -r requirements.txt

# Run all tests (requires credentials in .env)
pytest

# Run specific tests
pytest tests/test_robinhood.py -k test_name
pytest tests/test_gemini.py -k TestTrades

# Add -s flag for API call output to terminal
pytest -s

# Build documentation
cd docs && make html
```

## Testing Requirements

Testing requires real API credentials in `.env` file (copy from `.test.env` template):
```
robin_mfa=
robin_username=
robin_password=
gemini_account_key=
gemini_account_secret=
tda_encryption_passcode=
```

Tests use real API calls (no mocking). **Never test order placement** to prevent real trades.

## Code Contribution Guidelines

1. Separate commits for documentation vs code changes
2. Update `__init__.py` to import new functions
3. Update version number in `setup.py` (format XX.YY.ZZ where XX=major, YY=features, ZZ=bugfixes)
4. Write tests for new functionality (except order placement)

## Standard Usage Pattern

```python
import robin_stocks.robinhood as rh
import robin_stocks.gemini as gem
import robin_stocks.tda as tda

# Authentication examples
login = rh.login(username, password, mfa_code=totp)
gem.login(api_key, secret_key)
tda.login(encryption_passcode)
```

## Request Architecture

All APIs use consistent request patterns with:
- Pagination support ('pagination', 'results', 'indexzero')
- Exception catching with logging
- Graceful degradation (returns None/empty lists on errors)  
- Optional `info` parameter for data filtering
- Decorator-based authentication and input validation

## Security Considerations

- Pickle-based session persistence with device tokens
- Encrypted storage for sensitive credentials
- Environment variables for credential management
- HMAC signatures and OAuth2 flows with refresh tokens
- Device fingerprinting and request signing