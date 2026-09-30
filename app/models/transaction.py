# app/models/transaction.py
# HANGED (was Models/Transaction.py)
# REFS: 1.1 (Transaction fields), 2.2 (POST .../transfer body),
#       1.3 + 3.3 (branch_id on transactions), 1.4 (negative inputs)

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

def _two_decimals(value):
    if round(value, 2) != value:
        raise ValueError("amount can't have more than 2 decimal places")
    return value

# [1.1]
class Transaction(BaseModel):
    '''The Transaction model & what the API returns.'''
    id: int # WAS transaction_id
    type: str # types: DEPOSIT / WITHDRAWAL / TRANSFER
    from_account: str | None # WAS account_id_from (int); now an account_number
    to_account: str | None # WAS account_id_to (int); now an account_number
    amount: float
    branch_id: int # the branch the $ moved thru (can sum without a join)
    created_at: datetime # server-set: prevents backdating a transaction


# [2.2]
class TransferCreate(BaseModel):
    '''Body of POST /api/v1/transactions/transfer (process money transfer).'''
    from_account: str
    to_account: str
    amount: float = Field(..., gt=0)                        # [1.4] negative / zero amounts are rejected

    @field_validator("amount")
    @classmethod
    def _amount_two_decimals(cls, value):
        return _two_decimals(value)


# [1.1, 1.2, 2.2]
class TransactionCreate(BaseModel):
    '''Body of POST /api/v1/transactions (a DEPOSIT or a WITHDRAWAL).'''
    type: Literal["DEPOSIT", "WITHDRAWAL"]
    from_account: str | None = None # WITHDRAWAL: takes money OUT this acount)
    to_account: str | None = None # DEPOSIT: puts money INTO this account
    amount: float = Field(..., gt=0)

    @field_validator("type", mode="before")
    @classmethod
    def _accept_any_case(cls, value):
        return value.upper() if isinstance(value, str) else value

    @field_validator("amount")
    @classmethod
    def _amount_two_decimals(cls, value):
        return _two_decimals(value)

    @model_validator(mode="after")
    def _accounts_match_type(self):
        if self.type == "DEPOSIT" and (self.to_account is None or self.from_account is not None):
            raise ValueError("a DEPOSIT needs to_account (and no from_account)")
        if self.type == "WITHDRAWAL" and (self.from_account is None or self.to_account is not None):
            raise ValueError("a WITHDRAWAL needs from_account (and no to_account)")
        return self
