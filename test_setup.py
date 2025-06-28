#!/usr/bin/env python3
"""
Test script to verify Robin Stocks setup.
Run this after configuring your .env file.
"""

import os

from dotenv import load_dotenv

import robin_stocks.gemini as gem

# Load environment variables
load_dotenv()

print("🔍 Robin Stocks Setup Verification")
print("=" * 40)

# Check environment variables
print("\n📋 Checking environment configuration:")

# Robinhood
rh_user = os.getenv("robin_username")
rh_pass = os.getenv("robin_password")
if rh_user and rh_pass:
    print("✅ Robinhood credentials found")
    if rh_user == "your_email@example.com":
        print("   ⚠️  Using template values - please update!")
else:
    print("❌ Robinhood credentials missing")

# Gemini
gem_key = os.getenv("gemini_account_key")
gem_secret = os.getenv("gemini_account_secret")
if gem_key and gem_secret:
    print("✅ Gemini API keys found")
    if gem_key == "account-xxxxxxxxxxxxxxxx":
        print("   ⚠️  Using template values - please update!")
else:
    print("❌ Gemini API keys missing")

# TD Ameritrade
tda_pass = os.getenv("tda_encryption_passcode")
if tda_pass:
    print("✅ TD Ameritrade encryption passcode found")
    if tda_pass == "your_strong_encryption_password":
        print("   ⚠️  Using template values - please update!")
else:
    print("❌ TD Ameritrade encryption passcode missing")

# Check dry run mode
dry_run = os.getenv("dry_run_mode", "true").lower() == "true"
print(f"\n🛡️  Dry run mode: {'ENABLED' if dry_run else 'DISABLED'}")
if not dry_run:
    print("   ⚠️  WARNING: Live trading enabled!")

# Test API connections (only if credentials are real)
print("\n🔌 Testing API connections:")


def test_robinhood():
    """Test Robinhood connection."""
    try:
        if rh_user and rh_user != "your_email@example.com":
            print("   Testing Robinhood...")
            # Note: This will prompt for 2FA if enabled
            # rh.login(rh_user, rh_pass)
            # if rh.get_login_state():
            #     print("   ✅ Robinhood connection successful")
            # else:
            #     print("   ❌ Robinhood login failed")
            print("   ⏭️  Skipping live test - uncomment code to test")
        else:
            print("   ⏭️  Skipping Robinhood - no valid credentials")
    except Exception as e:
        print(f"   ❌ Robinhood error: {e}")


def test_gemini():
    """Test Gemini connection."""
    try:
        if gem_key and gem_key != "account-xxxxxxxxxxxxxxxx":
            print("   Testing Gemini...")
            sandbox = os.getenv("gemini_sandbox", "true").lower() == "true"
            gem.login(gem_key, gem_secret, sandbox=sandbox)
            if gem.get_login_state():
                print(
                    f"   ✅ Gemini connection successful ({'sandbox' if sandbox else 'live'} mode)"
                )
            else:
                print("   ❌ Gemini login failed")
        else:
            print("   ⏭️  Skipping Gemini - no valid credentials")
    except Exception as e:
        print(f"   ❌ Gemini error: {e}")


def test_tda():
    """Test TD Ameritrade connection."""
    try:
        if tda_pass and tda_pass != "your_strong_encryption_password":
            print("   Testing TD Ameritrade...")
            # This will fail if you haven't done the initial OAuth setup
            # tda.login(tda_pass)
            # if tda.get_login_state():
            #     print("   ✅ TD Ameritrade connection successful")
            # else:
            #     print("   ❌ TD Ameritrade login failed")
            print("   ⏭️  Skipping live test - requires initial OAuth setup")
        else:
            print("   ⏭️  Skipping TD Ameritrade - no valid credentials")
    except Exception as e:
        print(f"   ❌ TD Ameritrade error: {e}")


# Run tests
test_robinhood()
test_gemini()
test_tda()

# Show next steps
print("\n📚 Next Steps:")
print("1. Update .env with your real credentials")
print("2. For Robinhood: Have your 2FA ready")
print("3. For Gemini: Create API keys at https://exchange.gemini.com/settings/api")
print("4. For TD Ameritrade: Complete OAuth setup first")
print("5. Run example bots in examples/trading_bot_examples/")

print("\n💡 Quick test commands:")
print("   python3 test_setup.py                    # Run this test again")
print("   pytest tests/test_trading_bot.py -v     # Test trading logic")
print("   python3 examples/trading_bot_examples/basic_trading_bot.py")

print("\n⚠️  Remember: Always use dry_run_mode=true for testing!")
