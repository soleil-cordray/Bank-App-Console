from fastapi import HTTPException
from core import app
from Models.Transaction import TransactionResponse, TransactionCreate

@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate):
    # Implementation for creating a new transaction
    pass

@app.get("/transactions/", response_model=list[TransactionResponse])
def read_transactions():
    # Implementation for reading all transactions
    pass

@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def read_transaction(transaction_id: int):
    # Implementation for reading a specific transaction by ID
    pass

@app.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, transaction: TransactionCreate):
    # Implementation for updating a specific transaction by ID
    pass

@app.delete("/transactions/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(transaction_id: int):
    # Implementation for deleting a specific transaction by ID
    pass