"""An example on how to place an order and then cancel it."""

import os

from dotenv import load_dotenv

import robin_stocks.tda as tda

load_dotenv()

# login
tda.login(os.environ["TDA_ENCRYPTION_PASSCODE"])
# format the order payload
order = {
    "orderType": "MARKET",
    "session": "NORMAL",
    "duration": "DAY",
    "orderStrategyType": "SINGLE",
    "orderLegCollection": [
        {
            "instruction": "Buy",
            "quantity": 1,
            "instrument": {"symbol": "AMC", "assetType": "EQUITY"},
        }
    ],
}
data, err = tda.place_order(os.environ["TDA_ORDER_ACCOUNT"], order, True)
order_id = tda.get_order_number(data)
print("the order has been placed and the order id is ", order_id)
cancel, err = tda.cancel_order(os.environ["TDA_ORDER_ACCOUNT"], order_id, False)
print("the order has been cancelled")
print(cancel.headers)
