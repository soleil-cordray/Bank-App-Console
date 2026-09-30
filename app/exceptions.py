# app/exceptions.py
# NEW. Old services did `raise HTTPException(status_code=404, ...)`, making
# the SERVICE layer depend on HTTP (which belongs to the CONTROLLER layer).
# Now, services raise these exceptions, which main.py turns into HTTP responses
# REFS: 2.C (status codes 400 / 404, and the Controller -> Service ->
#            Repository layering: services must not know about HTTP)

class NotFoundError(Exception):
    """Something the caller asked for by ID / URL does not exist -> HTTP 404."""

class BadRequestError(Exception):
    """The request is invalid (bad data, broken business rule) -> HTTP 400."""

class UnauthorizedError(Exception):
    """Not logged in, or wrong email/password -> HTTP 401. [5A.2]"""
