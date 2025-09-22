
---

# Custodia

Educational backend project on **Django 5 + DRF**, where authentication and authorization are implemented **from scratch** (without djoser/simplejwt). The goal is to demonstrate understanding of JWT, middleware, sessions/tokens, and RBAC with ownership checks.

## Key Features

* **Authentication**

   * Registration via email + password (bcrypt)
   * Login → `access` and `refresh` JWT (PyJWT)
   * Refreshing access tokens
   * Logout (client-side)
   * Profile `/users/me` (GET, PATCH, DELETE soft delete: `is_active=false`)
   * Custom middleware: parses `Authorization: Bearer …`, validates JWT, assigns `request.user`
   * Custom DRF authenticator: trusts the user set by middleware

* **Authorization (RBAC + owner)**

   * Tables: `roles`, `business_elements`, `access_roles_rules`
   * Flags: `read(_all)`, `create`, `update(_all)`, `delete(_all)`
   * Custom DRF permission `RolePermission`, enforces ownership for update/delete
   * Admin API: CRUD for roles/elements/rules (only available to role `admin`)

* **Mock resources to demo 200/401/403**

   * `Goods` and `Orders` with `owner` field
   * Lists are filtered: without `read_all`, users only see their own
   * CRUD is RBAC-controlled

* **Docs and utilities**

   * OpenAPI: `/api/docs/` (Swagger), `/api/redoc/`
   * Fixtures for roles/elements/rules
   * Command `seed_demo` to populate demo users and data
   * Pytest smoke tests (auth + RBAC)
   * pre-commit: ruff, black, isort

## Tech Stack

Python 3.12, Django 5, DRF, PyJWT, bcrypt, drf-spectacular, PostgreSQL (prod), SQLite (dev), Docker Compose.

## Architecture

```
src/
apps/
  accounts/   # registration, login, JWT, profile, middleware, DRF auth backend
  authz/      # Role, BusinessElement, AccessRoleRule, permissions, admin API
  core/       # base abstractions (TimeStampedModel, OwnedModel), commands
  mock/       # Good, Order + CRUD
custodia/     # settings (base/dev/prod), urls
fixtures/     # roles/elements/rules
tests/        # pytest
```

### Access model (in a nutshell)

* User role is stored in `Profile.role` (FK to `Role`).
* For each `(role, business_element)` pair, there’s a row in `access_roles_rules`.
* Without `*_all` flags, access to other users’ objects is denied (checked by `owner_id`).

## Quickstart (dev, SQLite)

```bash
# select dev settings
export DJANGO_SETTINGS_MODULE=custodia.settings.dev  # Windows: $env:DJANGO_SETTINGS_MODULE="custodia.settings.dev"

pip install -r requirements.txt
python src/manage.py migrate

# load fixtures for roles/elements/rules
python src/manage.py loaddata \
  src/fixtures/authz_roles.json \
  src/fixtures/authz_elements.json \
  src/fixtures/authz_rules_admin_all.json \
  src/fixtures/authz_rules_user_manager.json \
  src/fixtures/authz_rules_orders_user_manager.json

# demo users and data (admin/user/manager, password: secret123)
python src/manage.py seed_demo

python src/manage.py runserver 0.0.0.0:8000
```

Open:

* Swagger: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
* ReDoc: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
* Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Run in Docker (prod, Postgres)

Files: `Dockerfile`, `compose.yaml`, `.env.prod` (contains `DJANGO_SETTINGS_MODULE=custodia.settings.prod` and `POSTGRES_*`).

```bash
docker compose --env-file .env.prod up --build
# then inside the web container:
docker compose exec web bash -lc "python src/manage.py loaddata \
  src/fixtures/authz_roles.json \
  src/fixtures/authz_elements.json \
  src/fixtures/authz_rules_admin_all.json \
  src/fixtures/authz_rules_user_manager.json \
  src/fixtures/authz_rules_orders_user_manager.json && \
  python src/manage.py seed_demo"
```

## Demo scenario (RBAC, paste as Raw in Postman)

```bash
# login (admin / user / manager)
curl -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"admin@local.com","password":"secret123"}'
curl -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"user@local.com","password":"secret123"}'
curl -X POST http://127.0.0.1:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"manager@local.com","password":"secret123"}'

# create goods as user and manager
curl -X POST http://127.0.0.1:8000/api/mock/goods -H "Authorization: Bearer <ACCESS_USER>" -H "Content-Type: application/json" -d '{"title":"Apple"}'
curl -X POST http://127.0.0.1:8000/api/mock/goods -H "Authorization: Bearer <ACCESS_MANAGER>" -H "Content-Type: application/json" -d '{"title":"Orange"}'

# user sees only their own
curl -X GET http://127.0.0.1:8000/api/mock/goods -H "Authorization: Bearer <ACCESS_USER>"

# manager sees all, but can update only their own
curl -X GET http://127.0.0.1:8000/api/mock/goods -H "Authorization: Bearer <ACCESS_MANAGER>"
curl -X PATCH http://127.0.0.1:8000/api/mock/goods/<ID_MANAGER_GOOD> -H "Authorization: Bearer <ACCESS_MANAGER>" -H "Content-Type: application/json" -d '{"title":"ManagerOwn"}'
curl -X PATCH http://127.0.0.1:8000/api/mock/goods/<ID_USER_GOOD> -H "Authorization: Bearer <ACCESS_MANAGER>" -H "Content-Type: application/json" -d '{"title":"Nope"}'  # 403

# admin can delete anything
curl -X DELETE http://127.0.0.1:8000/api/mock/goods/<ANY_ID> -H "Authorization: Bearer <ACCESS_ADMIN>"
```

## Endpoints

Auth:
`POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`
`GET|PATCH|DELETE /api/auth/users/me`

Mock:
`GET|POST /api/mock/goods`, `GET|PATCH|DELETE /api/mock/goods/{id}`
`GET|POST /api/mock/orders`, `GET|PATCH|DELETE /api/mock/orders/{id}`

AuthZ admin (admin role only):
`GET|POST /api/authz/roles`, `GET|PATCH|DELETE /api/authz/roles/{id}`
`GET|POST /api/authz/elements`, `GET|PATCH|DELETE /api/authz/elements/{id}`
`GET|POST /api/authz/rules`, `GET|PATCH|DELETE /api/authz/rules/{id}`

## Tests & Code Quality

```bash
pytest -q
ruff check src
black src && isort src
pre-commit install
```

## Notes

* Users created in Django admin won’t automatically get usable credentials. To log in, create via `/register` or run `seed_demo`.
* Role comes from `Profile.role`. `is_staff`/`is_superuser` only affect Django Admin, not RBAC for mock resources.
* Unauthenticated → 401; authenticated without permissions → 403.

## License

MIT

---