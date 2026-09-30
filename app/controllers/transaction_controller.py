# app/controllers/transaction_controller.py
# WAS Controllers/TransactionController.py, which was all `pass` stubs
# REFS: 2.2 (transfer), 2.3 (filters), 2.C

from datetime import date

from fastapi import APIRouter

from app.models.transaction import Transaction, TransactionCreate, TransferCreate
from app.services.transaction_service import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/transfer", response_model=Transaction, status_code=201)
def transfer_money(transfer: TransferCreate):
    # POST /api/v1/transactions/transfer (process money transfer) [2.2]
    return transaction_service.transfer(transfer)


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(transaction: TransactionCreate):
    # a DEPOSIT or WITHDRAWAL (see TransactionCreate)
    return transaction_service.create_transaction(transaction)


@router.get("", response_model=list[Transaction])
def read_transactions(start_date: date | None = None, type: str | None = None):
    # GET /api/v1/transactions?start_date=2026-01-01&type=TRANSFER [2.3]
    # `start_date` arrives as a real date
    # noqa: A002
    return transaction_service.get_all_transactions(start_date, type)


@router.get("/{id}", response_model=Transaction)
def read_transaction(id: int):
    # read one transaction [2.C]
    # noqa: A002
    return transaction_service.get_transaction(id)

# REMOVED: PUT and DELETE /transactions/{id} (see models/transaction.py)
