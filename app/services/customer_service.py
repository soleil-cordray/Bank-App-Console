# app/services/customer_service.py
# WAS Services/UserService.py
# REFS: 2.2 (the five customer endpoints), 1.1 (Accounts list)

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.customer import Customer, CustomerCreate, CustomerUpdate
from app.repositories.account_repository import account_repository
from app.repositories.branch_repository import branch_repository
from app.repositories.customer_repository import customer_repository


class CustomerService:
    def create_customer(self, customer: CustomerCreate) -> Customer:
        # POST /customers [2.2]
        self._check_branch_exists(customer.branch_id)
        saved = customer_repository.create(customer)
        return self._to_customer(saved)

    def get_all_customers(self) -> list[Customer]:                        #
        # GET /customers [2.2]
        return [self._to_customer(c) for c in customer_repository.get_all()]

    def get_customer(self, customer_id: int, user=None) -> Customer:
        # GET /customers/{id} [2.2]
        # OWN DATA [5A.3]: a CUSTOMER may only read their own profile
        if user is not None and user.role == "CUSTOMER" and user.customer_id != customer_id:
            raise ForbiddenError("You can only view your own profile")
        return self._to_customer(self._get_or_404(customer_id))

    def update_customer(self, customer_id: int, customer: CustomerUpdate) -> Customer:
        # PUT /customers/{id} [2.2]
        self._get_or_404(customer_id)
        changes = customer.model_dump(exclude_none=True)
        if "branch_id" in changes:
            self._check_branch_exists(changes["branch_id"])
        updated = customer_repository.update(customer_id, changes)
        return self._to_customer(updated)

    def deactivate_customer(self, customer_id: int) -> Customer:
        #  DELETE /customers/{id}
        self._get_or_404(customer_id)
        deactivated = customer_repository.deactivate(customer_id)
        account_repository.deactivate_by_owner(customer_id)
        return self._to_customer(deactivated)

    # HELPERS -----------------------------------------------------------------

    def _to_customer(self, document) -> Customer:
        # "accounts list" looked up when the customer is read
        accounts = account_repository.get_all({"owner_id": document["customer_id"]})
        document = {**document, "accounts_list": [a["account_number"] for a in accounts]}
        return Customer.model_validate(document)

    def _get_or_404(self, customer_id):
        customer = customer_repository.get_by_id(customer_id)
        if customer is None:
            raise NotFoundError("Customer not found.")
        return customer

    def _check_branch_exists(self, branch_id):
        # 400 (not 404): bad ID is in the request body, not the URL
        if branch_repository.get_by_id(branch_id) is None:
            raise BadRequestError(f"Branch {branch_id} does not exist")


customer_service = CustomerService()
