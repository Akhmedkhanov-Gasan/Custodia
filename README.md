````markdown
# Custodia — Authentication and Authorization System

## Overview

Custodia is a backend application that demonstrates a **custom implementation of authentication and authorization** mechanisms.
The goal is to show how login, logout, session/token management, and role-based access control (RBAC) can be built without relying on "out-of-the-box" solutions.

The project is designed for portfolio/demo purposes and illustrates the difference between **authentication (who you are)** and **authorization (what you are allowed to do)**.

## Features

- **User management**
  - Registration with email and password (stored securely with bcrypt)
  - Login with JWT access & refresh tokens
  - Logout with token invalidation
  - Update profile information
  - Soft-delete accounts (`is_active = False`)
- **Authentication**
  - JWT-based login/refresh system
  - Middleware to parse `Authorization: Bearer <token>` and attach `request.user`
- **Authorization**
  - Role-based access control (RBAC) with fine-grained permissions
  - Ownership rules: users can only modify their own resources unless granted `*_all` permissions
  - Admin API for managing roles, elements, and rules
  - Standard error handling:
    - `401 Unauthorized` for unauthenticated requests
    - `403 Forbidden` for authenticated users without required permissions
- **Mock resources**
  - Example endpoints for `goods` and `orders` to demonstrate permission checks
- **API schema**
  - OpenAPI 3.0 documentation with Swagger UI / ReDoc

## Database Schema

Main entities:

- `users` — application users (email, password, profile info, is_active flag)
- `roles` — user roles (`admin`, `manager`, `user`, `guest`)
- `business_elements` — application resources (`users`, `goods`, `orders`, `rules`)
- `access_roles_rules` — mapping of permissions per role and element:
  - `read_permission`, `read_all_permission`
  - `create_permission`
  - `update_permission`, `update_all_permission`
  - `delete_permission`, `delete_all_permission`

Example rules:
- **Admin** — full access to all resources
- **Manager** — read all, modify only own objects
- **User** — read and modify only own objects
- **Guest** — no access

## Endpoints

### Authentication
- `POST /api/auth/register` — create new account
- `POST /api/auth/login` — get access & refresh tokens
- `POST /api/auth/refresh` — refresh tokens
- `POST /api/auth/logout` — invalidate session
- `GET /api/users/me` — fetch current user
- `PATCH /api/users/me` — update current user
- `DELETE /api/users/me` — deactivate account

### Authorization (admin only)
- `GET /api/authz/roles`, `POST /api/authz/roles`
- `GET /api/authz/elements`, `POST /api/authz/elements`
- `GET /api/authz/rules`, `POST /api/authz/rules`

### Mock resources
- `GET /api/mock/goods`, `POST /api/mock/goods`
- `GET /api/mock/goods/{id}`, `PATCH /api/mock/goods/{id}`, `DELETE /api/mock/goods/{id}`
- `GET /api/mock/orders`, `POST /api/mock/orders`
- `GET /api/mock/orders/{id}`, `PATCH /api/mock/orders/{id}`, `DELETE /api/mock/orders/{id}`

## Installation

### Requirements
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 15

### Setup
```bash
git clone https://github.com/your-username/custodia.git
cd custodia
cp .env.example .env
docker compose up --build
````

### Apply migrations & load fixtures

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py loaddata fixtures/initial_data.json
```

## Usage

### Example demo flow

1. Register two users (`user` and `manager`)
2. Assign roles via admin API
3. Create goods/orders as both users
4. Test different permissions:

   * `user` sees only their goods
   * `manager` sees all goods but can update only own
   * `admin` can delete any goods
   * unauthenticated request → `401`

### API Docs

After starting the server, open:

* Swagger UI: `http://localhost:8000/api/schema/swagger/`
* ReDoc: `http://localhost:8000/api/schema/redoc/`

## Tech Stack

* Django 5 + DRF
* PostgreSQL 15
* bcrypt (password hashing)
* PyJWT (token handling)
* Docker Compose
* drf-spectacular (API docs)
* pytest + pytest-django (tests)
* black, isort, ruff (code style)

## License

MIT License