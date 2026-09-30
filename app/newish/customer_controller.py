# app/controllers/customer_controller.py
# WAS Controllers/UserController.py (which was all `pass` stubs)
# REFS: 2.2 (the five customer endpoints), 2.C (status codes 200 / 201)

# ACCESS: sign up = anyone; list / delete = admin; view = admin or self;
#         update / close request = the customer themselves

from fastapi import APIRouter, Depends

from app.auth import ADMIN_USERNAME, CurrentUser, admin_only, customer_only, get_current_user
from app.models.customer import Customer, CustomerCreate, CustomerUpdate
from app.services.customer_service import customer_service

# route is /customers (was /users/) & main.py adds /api/v1 prefix [2.2]
router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=Customer, status_code=201)
def create_customer(customer: CustomerCreate):
    # POST /api/v1/customers [2.2] (sign up; no login needed); 201 = created
    return customer_service.create_customer(customer, ADMIN_USERNAME)


@router.get("", response_model=list[Customer])
def read_customers(close_requested: bool | None = None, admin: CurrentUser = Depends(admin_only)):
    # GET /api/v1/customers (list customers) [2.2]; ?close_requested=true = pending closures
    return customer_service.get_all_customers(close_requested)


# /me routes come BEFORE /{id}, otherwise "me" would be read as an id
@router.get("/me", response_model=Customer)
def read_my_profile(user: CurrentUser = Depends(customer_only)):
    return customer_service.get_customer(user.customer_id)


@router.post("/me/close-request", response_model=Customer)
def request_closure(user: CurrentUser = Depends(customer_only)):
    # customers can't delete themselves; this asks the admin to do it
    return customer_service.request_closure(user.customer_id)


@router.get("/{id}", response_model=Customer)
def read_customer(id: int, user: CurrentUser = Depends(get_current_user)):
    # GET /api/v1/customers/{id} (get customer details) [2.2]
    return customer_service.get_customer(id, user.scope())


@router.put("/{id}", response_model=Customer)
def update_customer(id: int, customer: CustomerUpdate, user: CurrentUser = Depends(customer_only)):
    # [2.2] PUT /api/v1/customers/{id}    (Update info)
    return customer_service.update_customer(id, customer, user.customer_id)


@router.delete("/{id}", response_model=Customer)
def deactivate_customer(id: int, admin: CurrentUser = Depends(admin_only)):
    # [2.2] DELETE /api/v1/customers/{id} (Deactivate account)
    # noqa: A002
    return customer_service.deactivate_customer(id)
