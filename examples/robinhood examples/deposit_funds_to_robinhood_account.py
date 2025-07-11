import os

import pyotp
from dotenv import load_dotenv

import robin_stocks.robinhood as r

"""
This is an example script that will deposit money to your robinhood
account from the bank account of your choosing.

NOTE: View the two_factor_log_in.py script to see how automatic
two-factor loggin in works.
"""
### REPLACE ME
amount_to_deposit = "REPLACE-ME"
###
# Load environment variables
load_dotenv()
# Login using two-factor code
totp = pyotp.TOTP(os.environ["ROBIN_MFA"]).now()
login = r.login(
    os.environ["ROBIN_USERNAME"],
    os.environ["ROBIN_PASSWORD"],
    store_session=True,
    mfa_code=totp,
)
# Get the bank account information
bank_accounts = r.get_linked_bank_accounts()
account_names = r.filter_data(bank_accounts, "bank_account_nickname")
# set up default variable values for business logic
count = 1
valid_choice = False
bank_choice = -1
# Present the choices in a list starting at 1
# Feel free to delete this whole if loop and just select the ach_relationship url manually
if len(account_names) == 0:
    print("you do not have any linked bank accounts. Exiting...")
else:
    print("=====\navailable banks\n-----")
    for bank in account_names:
        print(f"{count}. {bank}")
        count += 1
    print(f"{count}. Cancel Deposit")
    print("-----")
    # Select a whole integer, if you select an invalid integer, code will prompt you again
    while not valid_choice:
        try:
            bank_choice = input(
                "Type in the number of the bank account you want to use below:\n"
            )
            bank_choice = int(bank_choice)
            if (
                bank_choice > 0 and bank_choice <= count
            ):  # allowable limits are 1 to the max number in list
                valid_choice = True
            else:
                raise ValueError
        except (ValueError, IndexError):
            # you could put the print statement outside the try-except block and have this
            # except have a simple 'pass' but then the "I'm sorry" statement would ALWAYS
            # print instead of printing only on failed entries. This is why I manually
            # raise the ValueError above. So that this statement only prints if the
            # int() function fails or I decide that the bank_choise is outside
            # allowable limits
            print("I'm sorry. That's not a valid integer choice, please try again")

if bank_choice == -1:
    pass  # exit condition
elif bank_choice == count:
    print("you chose to cancel. Exiting...")
else:
    ach_relationship = bank_accounts[bank_choice - 1]["url"]
    deposit = r.deposit_funds_to_robinhood_account(ach_relationship, amount_to_deposit)
    print(deposit)
