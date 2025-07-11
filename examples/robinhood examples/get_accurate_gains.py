import robin_stocks.robinhood as r

"""
Robinhood includes dividends as part of your net gain. This script removes
dividends from net gain to figure out how much your stocks/options have paid
off.

Note: load_portfolio_profile() contains some other useful breakdowns of equity.
Print profileData and see what other values you can play around with.

"""

#!!! Fill out username and password
username = ""
password = ""
#!!!

login = r.login(username, password)

profileData = r.load_portfolio_profile()
allTransactions = r.get_bank_transfers()
cardTransactions = r.get_card_transactions()

deposits = sum(
    float(x["amount"])
    for x in allTransactions
    if (x["direction"] == "deposit") and (x["state"] == "completed")
)
withdrawals = sum(
    float(x["amount"])
    for x in allTransactions
    if (x["direction"] == "withdraw") and (x["state"] == "completed")
)
debits = sum(
    float(x["amount"]["amount"])
    for x in cardTransactions
    if (x["direction"] == "debit" and (x["transaction_type"] == "settled"))
)
reversal_fees = sum(
    float(x["fees"])
    for x in allTransactions
    if (x["direction"] == "deposit") and (x["state"] == "reversed")
)

money_invested = deposits + reversal_fees - (withdrawals - debits)
dividends = r.get_total_dividends()
percentDividend = dividends / money_invested * 100

equity = float(profileData["extended_hours_equity"])
totalGainMinusDividends = equity - dividends - money_invested
percentGain = totalGainMinusDividends / money_invested * 100

print(f"The total money invested is {money_invested:.2f}")
print(f"The total equity is {equity:.2f}")
print(
    f"The net worth has increased {percentDividend:0.2}% due to dividends that amount to {dividends:0.2f}"
)
print(
    f"The net worth has increased {percentGain:0.3}% due to other gains that amount to {totalGainMinusDividends:0.2f}"
)
