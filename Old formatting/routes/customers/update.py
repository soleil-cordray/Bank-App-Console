# [EXPLAIN] Update operations for the logged-in customer: edit their details, deposit/withdraw, and open another bank account.
# [EXPLAIN] Every route uses /customers/me and customer_only, so a customer can only change their own data and the admin can't change anything.
from datetime import datetime
from typing import Literal, Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from auth import customer_only
from core import app

# [EXPLAIN] Every deposit/withdraw is logged here so the admin can review it.
# [SUGGEST] If read.py adds an admin "view transactions" route, move this list to core.py so both files share it.
transactions = []
transaction_id_counter = 1
bank_account_id_counter = 1


class CustomerUpdate(BaseModel):
    # Only send the fields you want to change. id and balance can't be edited here.
    name: Optional[str] = None
    postal_code: Optional[str] = None
    address: Optional[str] = None


class TransactionRequest(BaseModel):
    type: Literal["deposit", "withdraw"]   # anything else is rejected with a 422
    amount: float = Field(gt=0)            # no zero or negative amounts
    bank_account_id: Optional[int] = None  # None = the customer's main balance

    # The example /docs pre-fills. Without it, /docs guesses bank_account_id = 0, which doesn't exist.
    model_config = {"json_schema_extra": {"examples": [{"type": "deposit", "amount": 250}]}}


class BankAccountCreate(BaseModel):
    account_type: Literal["checking", "savings"]
    initial_deposit: float = Field(default=0.0, ge=0)


def find_bank_account(customer, bank_account_id):
    """Returns the dict whose "balance" we should change: the customer (main balance) or one extra bank account."""
    if bank_account_id is None:
        return customer
    for bank_account in customer.get("bank_accounts", []):
        if bank_account["id"] == bank_account_id:
            return bank_account
    raise HTTPException(status_code=404, detail="Bank account not found")


#update the logged-in customer's personal details
@app.put("/customers/me")
def update_my_details(changes: CustomerUpdate, customer=Depends(customer_only)):
    customer.update(changes.model_dump(exclude_none=True))
    return customer


#deposit or withdraw money
@app.post("/customers/me/transactions")
def make_transaction(transaction: TransactionRequest, customer=Depends(customer_only)):
    global transaction_id_counter

    bank_account = find_bank_account(customer, transaction.bank_account_id)

    if transaction.type == "withdraw":
        if transaction.amount > bank_account["balance"]:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        bank_account["balance"] -= transaction.amount
    else:
        bank_account["balance"] += transaction.amount
    bank_account["balance"] = round(bank_account["balance"], 2)  # keep money to cents

    record = {
        "id": transaction_id_counter,
        "customer_id": customer["id"],
        "bank_account_id": transaction.bank_account_id or "main",
        "type": transaction.type,
        "amount": transaction.amount,
        "balance_after": bank_account["balance"],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    transactions.append(record)
    transaction_id_counter += 1
    return record


#open another bank account (checking/savings) for the logged-in customer
@app.post("/customers/me/bank-accounts", status_code=201)
def add_bank_account(new_account: BankAccountCreate, customer=Depends(customer_only)):
    global bank_account_id_counter

    bank_account = {
        "id": bank_account_id_counter,
        "account_type": new_account.account_type,
        "balance": new_account.initial_deposit,
    }
    customer.setdefault("bank_accounts", []).append(bank_account)
    bank_account_id_counter += 1
    return bank_account
