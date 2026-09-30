# app/controllers/customer_controller.py
# WAS Controllers/UserController.py (which was all `pass` stubs)
# REFS: 2.2 (the five customer endpoints), 2.C (status codes 200 / 201)

from fastapi import APIRouter

from app.models.customer import Customer, CustomerCreate, CustomerUpdate
from app.services.customer_service import customer_service

# route is /customers (was /users/) & main.py adds /api/v1 prefix [2.2]
router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=Customer, status_code=201)
def create_customer(customer: CustomerCreate):
    # POST /api/v1/customers [2.2] (create customer profile); 201 = created
    return customer_service.create_customer(customer)


@router.get("", response_model=list[Customer])
def read_customers():
    # GET /api/v1/customers (list customers) [2.2]
    return customer_service.get_all_customers()

@router.get("/{id}", response_model=Customer)
def read_customer(id: int):
    # GET /api/v1/customers/{id} (get customer details) [2.2]
    return customer_service.get_customer(id)


@router.put("/{id}", response_model=Customer)
def update_customer(id: int, customer: CustomerUpdate):
    # [2.2] PUT /api/v1/customers/{id}    (Update info)
    return customer_service.update_customer(id, customer)


@router.delete("/{id}", response_model=Customer)
def deactivate_customer(id: int):
    # [2.2] DELETE /api/v1/customers/{id} (Deactivate account)
    # noqa: A002
    return customer_service.deactivate_customer(id)
