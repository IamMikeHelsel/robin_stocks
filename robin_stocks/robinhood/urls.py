"""Contains all the url endpoints for interacting with Robinhood API."""

from robin_stocks.robinhood.helper import id_for_chain, id_for_stock

# Login


def login_url():
    return "https://api.robinhood.com/oauth2/token/"


def challenge_url(challenge_id):
    return f"https://api.robinhood.com/challenge/{challenge_id}/respond/"


# Profiles


def account_profile_url(account_number=None):
    if account_number:
        return "https://api.robinhood.com/accounts/" + account_number
    else:
        return "https://api.robinhood.com/accounts/?default_to_all_accounts=true"


def basic_profile_url():
    return "https://api.robinhood.com/user/basic_info/"


def investment_profile_url():
    return "https://api.robinhood.com/user/investment_profile/"


def portfolio_profile_url(account_number=None):
    if account_number:
        return "https://api.robinhood.com/portfolios/" + account_number
    else:
        return "https://api.robinhood.com/portfolios/"


def security_profile_url():
    return "https://api.robinhood.com/user/additional_info/"


def user_profile_url():
    return "https://api.robinhood.com/user/"


def portfolis_historicals_url(account_number):
    return f"https://api.robinhood.com/portfolios/historicals/{account_number}/"


# Stocks


def earnings_url():
    return "https://api.robinhood.com/marketdata/earnings/"


def events_url():
    return "https://api.robinhood.com/options/events/"


def fundamentals_url():
    return "https://api.robinhood.com/fundamentals/"


def historicals_url():
    return "https://api.robinhood.com/quotes/historicals/"


def instruments_url():
    return "https://api.robinhood.com/instruments/"


def news_url(symbol):
    return f"https://api.robinhood.com/midlands/news/{symbol}/?"


def popularity_url(symbol):
    return f"https://api.robinhood.com/instruments/{id_for_stock(symbol)}/popularity/"


def quotes_url():
    return "https://api.robinhood.com/quotes/"


def ratings_url(symbol):
    return f"https://api.robinhood.com/midlands/ratings/{id_for_stock(symbol)}/"


def splits_url(symbol):
    return f"https://api.robinhood.com/instruments/{id_for_stock(symbol)}/splits/"


# account


def phoenix_url():
    return "https://phoenix.robinhood.com/accounts/unified"


def positions_url(account_number=None):
    if account_number:
        return "https://api.robinhood.com/positions/?account_number=" + account_number
    else:
        return "https://api.robinhood.com/positions/"


def banktransfers_url(direction=None):
    if direction == "received":
        return "https://api.robinhood.com/ach/received/transfers/"
    else:
        return "https://api.robinhood.com/ach/transfers/"


def cardtransactions_url():
    return "https://minerva.robinhood.com/history/transactions/"


def unifiedtransfers_url():
    return "https://bonfire.robinhood.com/paymenthub/unified_transfers/"


def daytrades_url(account):
    return f"https://api.robinhood.com/accounts/{account}/recent_day_trades/"


def dividends_url():
    return "https://api.robinhood.com/dividends/"


def documents_url():
    return "https://api.robinhood.com/documents/"


def withdrawl_url(bank_id):
    return f"https://api.robinhood.com/ach/relationships/{bank_id}/"


def linked_url(id=None, unlink=False):
    if unlink:
        return f"https://api.robinhood.com/ach/relationships/{id}/unlink/"
    if id:
        return f"https://api.robinhood.com/ach/relationships/{id}/"
    else:
        return "https://api.robinhood.com/ach/relationships/"


def margin_url():
    return "https://api.robinhood.com/margin/calls/"


def margininterest_url():
    return "https://api.robinhood.com/cash_journal/margin_interest_charges/"


def notifications_url(tracker=False):
    if tracker:
        return "https://api.robinhood.com/midlands/notifications/notification_tracker/"
    else:
        return "https://api.robinhood.com/notifications/devices/"


def referral_url():
    return "https://api.robinhood.com/midlands/referral/"


def stockloan_url():
    return "https://api.robinhood.com/accounts/stock_loan_payments/"


def interest_url():
    return "https://api.robinhood.com/accounts/sweeps/"


def subscription_url():
    return "https://api.robinhood.com/subscription/subscription_fees/"


def wiretransfers_url():
    return "https://api.robinhood.com/wire/transfers"


def watchlists_url(name=None, add=False):
    if name:
        return "https://api.robinhood.com/midlands/lists/items/"
    else:
        return "https://api.robinhood.com/midlands/lists/default/"


# markets


def currency_url():
    return "https://nummus.robinhood.com/currency_pairs/"


def markets_url():
    return "https://api.robinhood.com/markets/"


def market_hours_url(market, date):
    return f"https://api.robinhood.com/markets/{market}/hours/{date}/"


def movers_sp500_url():
    return "https://api.robinhood.com/midlands/movers/sp500/"


def get_100_most_popular_url():
    return "https://api.robinhood.com/midlands/tags/tag/100-most-popular/"


def movers_top_url():
    return "https://api.robinhood.com/midlands/tags/tag/top-movers/"


def market_category_url(category):
    return f"https://api.robinhood.com/midlands/tags/tag/{category}/"


# options


def aggregate_url(account_number):
    if account_number:
        return (
            "https://api.robinhood.com/options/aggregate_positions/?account_numbers="
            + account_number
        )
    else:
        return "https://api.robinhood.com/options/aggregate_positions/"


def chains_url(symbol):
    return f"https://api.robinhood.com/options/chains/{id_for_chain(symbol)}/"


def option_historicals_url(id):
    return f"https://api.robinhood.com/marketdata/options/historicals/{id}/"


def option_instruments_url(id=None):
    if id:
        return f"https://api.robinhood.com/options/instruments/{id}/"
    else:
        return "https://api.robinhood.com/options/instruments/"


def option_orders_url(orderID=None, account_number=None, start_date=None):
    url = "https://api.robinhood.com/options/orders/"
    if orderID:
        url += f"{orderID}/"
    query_build = []
    if account_number:
        query_build.append(f"account_numbers={account_number}")
    if start_date:
        query_build.append(f"updated_at[gte]={start_date}")

    if query_build:
        for index, value in enumerate(query_build):
            if index == 0:
                url += "?" + value
            else:
                url += "&" + value

    return url


def option_positions_url(account_number):
    if account_number:
        return (
            "https://api.robinhood.com/options/positions/?account_numbers="
            + account_number
        )
    else:
        return "https://api.robinhood.com/options/positions/"


def marketdata_options_url():
    return "https://api.robinhood.com/marketdata/options/"


# pricebook


def marketdata_quotes_url(id):
    return f"https://api.robinhood.com/marketdata/quotes/{id}/"


def marketdata_pricebook_url(id):
    return f"https://api.robinhood.com/marketdata/pricebook/snapshots/{id}/"


# crypto


def order_crypto_url():
    return "https://nummus.robinhood.com/orders/"


def crypto_account_url():
    return "https://nummus.robinhood.com/accounts/"


def crypto_currency_pairs_url():
    return "https://nummus.robinhood.com/currency_pairs/"


def crypto_quote_url(id):
    return f"https://api.robinhood.com/marketdata/forex/quotes/{id}/"


def crypto_holdings_url():
    return "https://nummus.robinhood.com/holdings/"


def crypto_historical_url(id):
    return f"https://api.robinhood.com/marketdata/forex/historicals/{id}/"


def crypto_orders_url(orderID=None):
    if orderID:
        return f"https://nummus.robinhood.com/orders/{orderID}/"
    else:
        return "https://nummus.robinhood.com/orders/"


def crypto_cancel_url(id):
    return f"https://nummus.robinhood.com/orders/{id}/cancel/"


# orders


def cancel_url(url):
    return f"https://api.robinhood.com/orders/{url}/cancel/"


def option_cancel_url(id):
    return f"https://api.robinhood.com/options/orders/{id}/cancel/"


def orders_url(orderID=None, account_number=None, start_date=None):
    url = "https://api.robinhood.com/orders/"
    if orderID:
        url += f"{orderID}/"

    query_build = []
    if account_number:
        query_build.append(f"account_numbers={account_number}")
    if start_date:
        query_build.append(f"updated_at[gte]={start_date}")

    if query_build:
        for index, value in enumerate(query_build):
            if index == 0:
                url += "?" + value
            else:
                url += "&" + value

    return url
