# app/dependencies.py
# NEW. FastAPI "dependencies" that protect routes.
# A route asks for one of these, and FastAPI runs it before the route:
#   - get_current_user: reads + checks the Bearer token -> 401 if bad
#   - require_roles(...): also checks the role          -> 403 if not allowed
# REFS: 5A.2 (token verification middleware), 5A.3 (RBAC)

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.auth import CurrentUser
from app.security import decode_access_token
from app.services.auth_service import auth_service

# BEARER TOKEN [5A.2]
# - reads the "Authorization: Bearer <token>" header
# - tokenUrl adds the "Authorize" button to Swagger (/docs),
#   which logs in through POST /api/v1/auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _unauthorized(detail):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    '''Who is calling? 401 if the token is missing, forged, or expired.'''
    try:
        payload = decode_access_token(token)
        login_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token expired. Log in again.")
    except (jwt.PyJWTError, ValueError, KeyError):
        raise _unauthorized("Invalid token")

    # the token is real, but the login may have been deactivated since
    login = auth_service.get_login(login_id)
    if login is None:
        raise _unauthorized("This login no longer exists")
    return CurrentUser.model_validate(login)


def require_roles(*roles):
    '''Only let these roles in. 403 for anyone else. [5A.3]

    Usage on a route:  user: CurrentUser = Depends(require_roles("ADMIN"))
    '''
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{user.role} can't do this. Allowed: {', '.join(roles)}",
            )
        return user
    return checker


# ROLE GROUPS: used across the controllers
ALL_ROLES = ("CUSTOMER", "TELLER", "BRANCH_MANAGER", "ADMIN")
STAFF = ("TELLER", "BRANCH_MANAGER", "ADMIN")
