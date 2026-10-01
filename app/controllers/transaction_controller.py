# app/controllers/transaction_controller.py
# WAS Controllers/TransactionController.py, which was all `pass` stubs
# REFS: 2.2 (transfer), 2.3 (filters), 2.C

from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import ALL_ROLES, STAFF, require_roles
from app.models.auth import CurrentUser

from app.models.transaction import Transaction, TransactionCreate, TransferCreate
from app.services.transaction_service import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/transfer", response_model=Transaction, status_code=201)
def transfer_money(transfer: TransferCreate, user: CurrentUser = Depends(require_roles("CUSTOMER", "ADMIN"))):
    # WHO [5A.3]: a CUSTOMER, only FROM their OWN account (checked in the service)
    # POST /api/v1/transactions/transfer (process money transfer) [2.2]
    return transaction_service.transfer(transfer, user)


@router.post("", response_model=Transaction, status_code=201)
def create_transaction(transaction: TransactionCreate, _: CurrentUser = Depends(require_roles("TELLER", "ADMIN"))):
    # WHO [5A.3]: a TELLER deposits / withdraws on behalf of customers
    # a DEPOSIT or WITHDRAWAL (see TransactionCreate)
    return transaction_service.create_transaction(transaction)


@router.get("", response_model=list[Transaction])
def read_transactions(start_date: date | None = None, type: str | None = None,
                      user: CurrentUser = Depends(require_roles(*ALL_ROLES))):
    # WHO [5A.3]: staff see all; a CUSTOMER only sees their OWN accounts' transactions
    # GET /api/v1/transactions?start_date=2026-01-01&type=TRANSFER [2.3]
    # `start_date` arrives as a real date
    # noqa: A002
    return transaction_service.get_all_transactions(start_date, type, user)


@router.get("/{id}", response_model=Transaction)
def read_transaction(id: int, user: CurrentUser = Depends(require_roles(*ALL_ROLES))):
    # WHO [5A.3]: staff, or a CUSTOMER if it touches their OWN account
    # read one transaction [2.C]
    # noqa: A002
    return transaction_service.get_transaction(id, user)

# REMOVED: PUT and DELETE /transactions/{id} (see models/transaction.py)
