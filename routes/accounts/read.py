from fastapi import HTTPException
from core import AccountRead, app, accounts

@app.get("/accounts", response_model=list[AccountRead])
def get_accounts():
    return accounts

@app.get("/accounts/{account_id}", response_model=AccountRead)
def get_account(account_id: int):
    for account in accounts:
        if account["id"] == account_id:
            return account
    raise HTTPException(status_code=404, detail="Account not found")