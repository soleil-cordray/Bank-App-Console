
import core
from fastapi import HTTPException
from core import app, accounts, AccountCreate


@app.post("/accounts", status_code=201)
def create_account(account: AccountCreate):
    

    for existing_account in accounts:
        if existing_account["username"] == account.username:
            raise HTTPException(status_code=400, detail="Username already exists")

    new_account = {
    
        "id": core.account_id_counter,
        "username": account.username,
        "password": account.password,
        "account_type": account.account_type,
        "customer_id": account.customer_id,
    }

    accounts.append(new_account)
    
    core.account_id_counter += 1

    return new_account
