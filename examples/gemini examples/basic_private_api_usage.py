"""The most basic way to use the Private API. I recommend renaming the file .test.env
to .env and filling out the gemini api key information. The dotenv package loads the .env (or .test.env)
file and the os.environ() function reads the values from the file.ß
"""

import os

from dotenv import load_dotenv

import robin_stocks.gemini as g

##
ticker = "btcusd"
##
g.login(os.environ["GEMINI_ACCOUNT_KEY"], os.environ["GEMINI_ACCOUNT_SECRET"])
my_trades, error = g.get_trades_for_crypto(ticker, jsonify=True)
if error:
    print("oh my an error")
else:
    print("no errors here")
print(my_trades)
