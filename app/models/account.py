# app/models/account.py
# CHANGED (was Models/Account.py, which held only Pydantic schemas)
# REFS: 1.1 (Account fields), 1.2 (the three classes),
#       1.C (OOP concepts, transfer limit, non-negative deposits),
#       1.4 (negative inputs), 2.3 (branch_id on accounts),
#       2.2 (POST /accounts body)

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator

# -----------------------------------------------------------------------------
# CLASSES [1.2]
# Account / Savings Account / CheckingAccount
# -----------------------------------------------------------------------------

class Account:
    '''Base Class: Everything every kind of account can do.'''

    # STRUCTURE [1.1] ---------------------------------------------------------

    TRANSFER_LIMIT = 10_000.00 # largest single transfer
    type = None # subclasses set type

    def __init__(self, account_number, owner_id, branch_id, balance=0.0):
        self.account_number = account_number
        self.owner_id = owner_id # the owner's customer_id
        self.branch_id = branch_id # needed for ?branch_id= [2.3]

        # ENCAPSULATION [1.C]: the leading underscore means "private"
        # - reached only through get_balance()
        # - changed only through deposit() / withdraw().
        self._balance = round(balance, 2)

    # NAMED METHODS [1.2] -----------------------------------------------------

    def get_balance(self):
        return self._balance

    def deposit(self, amount):
        # "non-negative deposits" [1.C], "negative inputs" [1.4]
        self.check_amount(amount)
        self._balance = round(self._balance + amount, 2)

    def withdraw(self, amount):
        self._check_amount(amount) # "negative inputs" [1.4]
        new_balance = round(self._balance - amount, 2)
        # POLYMORPHISM [1.C]:  lowest_allowed_balance() = the only difference
        # between account types (each subclass has their own)
        # - same interface
        # - different treatment
        if new_balance < self.lowest_allowed_balance():
            raise ValueError(
                f"INSUFFICIENT FUNDS. This would leave {new_balance:.2f}, "
                f"but the lowest allowed balance is {self.lowest_allowed_balance():.2f}."
            )
        self._balance = new_balance

    def lowest_allowed_balance(self):
        # the rule subclasses override (polymorphism)
        return 0.0

    # HELPERS -----------------------------------------------------------------

    @staticmethod
    def _check_amount(amount):
        # not amount > 0: rejects nan, which amount <= 0 would allow
        if not amount > 0:
            raise ValueError("amount must be greater than zero.")

    def validate_opening_balance(self):
        # a savings account cannot be opened with < its minimum balance
        if self._balance < self.lowest_allowed_balance():
            raise ValueError(
                f"A {self.type} account needs an opening balance of at least "
                        f"{self.lowest_allowed_balance():.2f}."
            )

    def to_document(self):
        # the dict that gets saved in MongoDB
        return {
            "account_number": self.account_number,
            "type": self.type,
            "balance": self._balance,
            "owner_id": self.owner_id,
            "branch_id": self.branch_id,
        }

    @classmethod
    def from_document(cls, document):
        # rebuild the right subclass from a saved document
        account_class = ACCOUNT_TYPES[document["type"]]
        return account_class(document["account_number"], document["owner_id"],
               document["branch_id"], document["balance"])

    @classmethod
    def new(cls, type, owner_id, branch_id, balance):
        # build new account (no account_number yet; repository generates it)
        account = ACCOUNT_TYPES[type](None, owner_id, branch_id, balance)
        account.validate_opening_balance()
        return account


class SavingsAccount(Account):
    '''Extends Account: type=SAVINGS, enforces minimum balance'''
    type = "SAVINGS"
    MINIMUM_BALANCE = 100.00

    # INHERITANCE [1.C]: inherits deposit/withdraw/get_balance, adds ONE rule
    def lowest_allowed_balance(self):
        # must never drop below the minimum
        return self.MINIMUM_BALANCE


class CheckingAccount(Account):
    '''Extends Account: type=SAVINGS, enforces minimum balance'''
    type = "CHECKING"
    OVERDRAFT_LIMIT = 500.00 # "overdraft limit logic" [1.2]

    # INHERITANCE [1.C]: inherits deposit/withdraw/get_balance, adds ONE rule
    def lowest_allowed_balance(self):
        # may go negative, but only down to -500
        return -self.OVERDRAFT_LIMIT


# SUB-CLASS TYPE HANDLING
ACCOUNT_TYPES = {"CHECKING": CheckingAccount, "SAVINGS": SavingsAccount}

# -----------------------------------------------------------------------------
# API SCHEMAS
# the Pydantic schemas that describe the JSON going in and out of the API
# -----------------------------------------------------------------------------

def _two_decimals(value):
    # money has cents, not fractions of a cent
    if round(value, 2) != value:
        raise ValueError("amounts can't have more than 2 decimal places")
    return value

class AccountCreate(BaseModel):
    '''Body of POST /api/v1/accounts (open new acount).'''
    owner_id: int = Field(..., gt=0) # WAS user_id [1.1]
    type: Literal["CHECKING", "SAVINGS"] # WAS account_type [1.1]
    branch_id: int = Field(..., gt=0) # ADDED [2.3]
    balance: float = Field(0.0, ge=0) # never negative [1.4]
    # REMOVED account_number (now server-generated)

    @field_validator("type", mode="before")
    @classmethod
    def _accept_any_case(cls, value):
        # "savings" -> "SAVINGS"
        return value.upper() if isinstance(value, str) else value

    @field_validator("balance")
    @classmethod
    def _balance_two_decimals(cls, value):
        # numerical precision
        return _two_decimals(value)

class AccountResponse(BaseModel):
    '''What the API returns for an account.'''
    # REMOVED account_id (accounts identified by account_number)
    account_number: str
    type: str
    balance: float
    owner_id: int
    branch_id: int
    created_at: datetime # the indexed field [3.1]
    is_active: bool

    @field_validator("balance")
    @classmethod
    def _round_balance(cls, value):
        # hides float noise from repeated $inc
        return round(value, 2)
