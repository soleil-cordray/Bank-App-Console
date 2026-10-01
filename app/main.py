# app/main.py
# WAS main.py + core.py; core.py is deleted, its one line lives here now
# REFS: 2.1 ("main.py: Entry Point"), 2.2 (/api/v1 prefix),
#       2.C (status codes 400 / 404)

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.controllers import (
    account_controller,
    auth_controller,
    branch_controller,
    customer_controller,
    transaction_controller,
)
from app.database import create_indexes, verify_connection
from app.exceptions import BadRequestError, ForbiddenError, NotFoundError, UnauthorizedError, ForbiddenError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # runs once when the server starts:
    # - fail fast if MongoDB is not running [not in rubric]
    # - then make sure the indexes exist [3.1]
    verify_connection()
    create_indexes()
    yield


# FRAMEWORK: this project uses FastAPI [2.C]
app = FastAPI(title="Bank-App Console", lifespan=lifespan)

# PREFIX: every endpoint starts with /api/v1 prefix, added here
for controller in (auth_controller, customer_controller, account_controller, transaction_controller, branch_controller):
    app.include_router(controller.router, prefix="/api/v1")


# CONVERT: services' exceptions into the HTTP status codes 2.C lists
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, error: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(BadRequestError)
async def bad_request_handler(request: Request, error: BadRequestError):
    return JSONResponse(status_code=400, content={"detail": str(error)})


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, error: UnauthorizedError):
    # 401 = not logged in / wrong email or password [5A.2]
    return JSONResponse(status_code=401, content={"detail": str(error)}, headers={"WWW-Authenticate": "Bearer"})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, error: RequestValidationError):
    # FastAPI's answer to a badly-formed body = 422,
    # which is not one of the codes 2.C lists (200, 201, 400, 404, 500)
    # - reporting those as 400 (Bad Request) keeps the API inside that list
    # - workshop does not say which code a malformed body should get
    return JSONResponse(status_code=400, content={"detail": jsonable_encoder(error.errors())})

# 401 / 403 come from app/dependencies.py (bad token / wrong role) [5A]
# 200 = OK & 201 = created are set on the routes themselves,
# 500 needs no code: FastAPI already answers 500 for any error nobody handled

@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, error: ForbiddenError):
    # logged in, but not allowed (e.g. someone else's account) -> 403
    return JSONResponse(status_code=403, content={"detail": str(error)})
