# [EXPLAIN] Entry point. uvicorn runs `main:app`, so `app` must be importable from this file.
from core import app  # uvicorn looks for `app` in this file

# [EXPLAIN] Each import below executes that route file, and the decorators inside it register the routes on `app`. That side effect is the only reason the routes exist.
# [SUGGEST] If someone adds a route file but forgets its import line here, the route silently 404s. Two safer options: auto-discover route modules with pkgutil, or switch to APIRouter and app.include_router(...), which is explicit.
# [SUGGEST] Linters flag these imports as unused. If that bothers you, add `# noqa: F401` to each line.
# Importing each route file registers its routes on `app`.
# Add one line here whenever you create a new route file.
import routes.customers.read
import routes.customers.create
import routes.customers.update
import routes.customers.delete
import routes.accounts.create
