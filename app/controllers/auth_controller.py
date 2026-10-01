# app/controllers/auth_controller.py
# NEW. Login endpoints.
# REFS: 5A.1 (registration + login), 5A.2 (token), 5A.3 (staff roles)

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_current_user, require_roles
from app.models.auth import CurrentUser, Login, RegisterRequest, StaffLoginCreate, Token
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Login, status_code=201)
def register(request: RegisterRequest):
    # POST /api/v1/auth/register  (public: a customer creates their login)
    return auth_service.register(request)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    # POST /api/v1/auth/login  (public)
    # sent as a form (username + password), which is the OAuth2 standard
    # and what Swagger's "Authorize" button sends; username = email
    return auth_service.login(form.username, form.password)


@router.get("/me", response_model=CurrentUser)
def who_am_i(user: CurrentUser = Depends(get_current_user)):
    # GET /api/v1/auth/me  (any logged-in user: shows what the token says)
    return user


@router.post("/staff", response_model=Login, status_code=201)
def create_staff_login(request: StaffLoginCreate, _: CurrentUser = Depends(require_roles("ADMIN"))):
    # POST /api/v1/auth/staff  (ADMIN only: make TELLER / BRANCH_MANAGER / ADMIN logins)
    return auth_service.create_staff_login(request)
