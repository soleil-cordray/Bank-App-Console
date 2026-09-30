# app/services/customer_service.py
# WAS Services/UserService.py
# REFS: 2.2 (the five customer endpoints), 1.1 (Accounts list)

# PERMISSIONS: `caller_id` = the logged-in customer's ID (None = the admin).
# A customer may only see / change their own profile.

from pymongo.errors import DuplicateKeyError

from app.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.customer import Customer, CustomerCreate, CustomerUpdate
from app.repositories.account_repository import account_repository
from app.repositories.branch_repository import branch_repository
from app.repositories.customer_repository import customer_repository


class CustomerService:
    def create_customer(self, customer: CustomerCreate, admin_username: str) -> Customer:
        # POST /customers [2.2] (sign up: anyone can create their own profile + login)
        self._check_branch_exists(customer.branch_id)
        if customer.username.lower() == admin_username.lower():
            raise BadRequestError("That username is reserved")
        try:
            saved = customer_repository.create(customer)
        except DuplicateKeyError:
            # database.py has a unique index on username; rejects repeats
            raise BadRequestError("Username is already taken")
        return self._to_customer(saved)

    def get_all_customers(self, close_requested: bool | None = None) -> list[Customer]:
        # GET /customers [2.2] (admin); ?close_requested=true lists pending closures
        filters = {}
        if close_requested is not None:
            filters["close_requested"] = True if close_requested else {"$ne": True}
        return [self._to_customer(c) for c in customer_repository.get_all(filters)]

    def get_customer(self, customer_id: int, caller_id: int | None = None) -> Customer:
        # GET /customers/{id} [2.2] (admin: anyone; customer: only themselves)
        customer = self._get_or_404(customer_id)
        self._check_is_caller(customer_id, caller_id)
        return self._to_customer(customer)

    def update_customer(self, customer_id: int, customer: CustomerUpdate, caller_id: int) -> Customer:
        # PUT /customers/{id} [2.2] (only the customer themselves)
        self._get_or_404(customer_id)
        self._check_is_caller(customer_id, caller_id)
        changes = customer.model_dump(exclude_none=True)
        if "branch_id" in changes:
            self._check_branch_exists(changes["branch_id"])
        updated = customer_repository.update(customer_id, changes)
        return self._to_customer(updated)

    def request_closure(self, customer_id: int) -> Customer:
        # a customer can't delete themselves; they ask, and the admin decides
        self._get_or_404(customer_id)
        updated = customer_repository.update(customer_id, {"close_requested": True})
        return self._to_customer(updated)

    def deactivate_customer(self, customer_id: int) -> Customer:
        #  DELETE /customers/{id} (admin only)
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

    @staticmethod
    def _check_is_caller(customer_id, caller_id):
        # caller_id None = admin (allowed); otherwise it must be their own profile
        if caller_id is not None and caller_id != customer_id:
            raise ForbiddenError("You can only access your own profile")

    def _check_branch_exists(self, branch_id):
        # 400 (not 404): bad ID is in the request body, not the URL
        if branch_repository.get_by_id(branch_id) is None:
            raise BadRequestError(f"Branch {branch_id} does not exist")


customer_service = CustomerService()
