# Developer Guide

Quick onboarding and contribution guide for the FastAPI E-Commerce API project.

## Project overview

- Framework: FastAPI
- Async ORM: SQLAlchemy 2.x (asyncio)
- DB driver: asyncpg (Postgres)
- Validation: Pydantic v2
- Containerization: Docker + docker-compose

This repository implements a small REST API (categories resource) using a service-controller-router pattern and a simple `APIResponse` wrapper.

## Repository structure (important files)

- `app/` - main application package
  - `main.py` - FastAPI application factory and lifespan hook (creates DB tables on startup)
  - `config.py` - settings (Pydantic Settings)
  - `database.py` - SQLAlchemy async engine, `AsyncSessionLocal`, `Base` and `get_db` dependency
  - `core/response.py` - `APIResponse` model used by controllers
  - `categories/` - domain module for categories
    - `model.py` - SQLAlchemy model
    - `schemas.py` - Pydantic request/response schemas
    - `service.py` - business logic / DB access using `AsyncSession`
    - `controller.py` - HTTP-level coordination, returns `APIResponse` and raises HTTPExceptions
    - `router.py` - FastAPI router mounted at `/api/v1/categories`
- `requirements.txt` - python dependencies
- `Dockerfile`, `docker-compose.yml` - container and orchestration config
- `.env` - local environment variables (not committed in some setups; present here)

## Key design patterns & conventions

- Async-first: use `AsyncSession` and async/await in services and controllers.
- Layers: router -> controller -> service -> model
- Controllers return `APIResponse` for consistent API shape:
  - `{ success: bool, message: str, data: any | null }`
- Database schema is created automatically at app startup via `Base.metadata.create_all` in `main.py` lifespan.
- Pydantic v2: schema classes use `model_dump`, `model_validate` and ConfigDict where needed.

## Local development setup (minimal)

Prerequisites:
- Python 3.11
- PostgreSQL (local or via Docker)
- git

1. Clone the repo

   git clone <repo-url>
   cd fastapi

2. Create & activate a virtual environment

   python -m venv .venv
   source .venv/bin/activate

3. Install dependencies

   pip install -r requirements.txt

4. Configure environment

- Copy `.env.example` to `.env` if present and adjust values. The repo includes `.env` with defaults.
- Ensure `DATABASE_URL` points to a running Postgres instance. Example local URL (matches .env):

  postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce_db

5. Start Postgres (choose one)

- Option A: Run Postgres locally (install Postgres and create DB/user).

- Option B: Use Docker Compose to spin up Postgres and other services:

  docker-compose up -d postgres

  or run full stack (api, db, redis, nginx):

  docker-compose up -d

> Note: `docker-compose.dev.yml` exists for a dev-only setup but references `Dockerfile.dev` which may not be present. Use `docker-compose.yml` for the full stack.

6. Run the app locally

- Run with uvicorn (development):

  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

- Run using FastAPI CLI (convenience wrapper)

  fastapi dev app.main:app --reload --host 0.0.0.0 --port 8000

  or using the module form:

  python -m fastapi dev app.main:app --reload --host 0.0.0.0 --port 8000

  Notes:
  - The `fastapi` CLI is installed with the FastAPI package included in `requirements.txt`.
  - `fastapi dev` is a convenience wrapper around `uvicorn` that starts the app with recommended development settings (auto-reload, helpful logging).
  - If `fastapi` is not found, ensure your virtual environment is activated and FastAPI is installed (`pip install fastapi`) or use the `uvicorn` command above.

- Or use Docker as defined in `Dockerfile`/`docker-compose.yml`.

7. Health check

- Open: http://localhost:8000/api/v1/health

Expect JSON stating `status: healthy` when DB reachable.

## Running with Docker (full stack)

1. Ensure Docker is installed.
2. Copy or set environment variables (see `.env`).
3. Start stack:

   docker-compose up -d --build

4. Tail logs:

   docker-compose logs -f api

5. Stop stack:

   docker-compose down

## Debugging tips

- Database errors: check container logs or local Postgres logs. The health endpoint exercises a `SELECT 1` to verify connectivity.
- SQLAlchemy echo: controlled by `DEBUG` setting and `settings.DATABASE_URL`. Set `DEBUG=True` in `.env` to see SQL logs.
- If tables are not created, verify `main.py` lifespan is running and `Base.metadata.create_all` executed against the correct DB URL.

## How to add a new feature (complete step-by-step)

Follow these steps to add a new resource (example: Products). The project uses the same pattern as `categories`.

1. Create a new package directory

   app/products/

2. Files to create (skeleton names):

- `app/products/model.py` - SQLAlchemy model
- `app/products/schemas.py` - Pydantic schemas (Create, Update, Response)
- `app/products/service.py` - Database operations and business logic
- `app/products/controller.py` - HTTP logic, translate service results to `APIResponse` and raise `HTTPException` on errors
- `app/products/router.py` - FastAPI router and route definitions

3. Implement model

- Use `app.database.Base` as the declarative base.
- Define columns, relationships, indexes and timestamps like `categories/model.py`.

4. Implement schemas

- `CreateSchema` and `UpdateSchema` should be Pydantic v2 models.
- `Response` model should set `model_config = ConfigDict(from_attributes=True)` to allow returning SQLAlchemy objects via `CategoryResponse.model_validate(category)` pattern.

5. Implement service

- Use `AsyncSession` as dependency and pattern in `CategoryService`.
- Provide methods: `get_all`, `get_by_id`, `get_by_<unique_field>`, `create`, `update`, `delete`.
- Raise `ValueError` in service on business validation conflicts (controllers map to HTTP 409).

6. Implement controller

- Mirror `CategoryController` structure: construct with `db`, call service methods, raise `HTTPException` for not found, conflicts, etc., and return `APIResponse.ok(...)`.

7. Implement router

- Create FastAPI `APIRouter(prefix="/resource", tags=["Resource"])` and define endpoints:
  - GET / -> list
  - GET /{id} -> retrieve
  - POST / -> create (status_code=201)
  - PUT /{id} -> update
  - DELETE /{id} -> delete
- Use dependency injection: `db: AsyncSession = Depends(get_db)` on each endpoint.

8. Register router

- Open `app/main.py` and add the router import and include it on the FastAPI app similar to categories:

  from app.products.router import router as products_router

  app.include_router(products_router, prefix="/api/v1")

9. Create database (dev)

- Because `main.py` calls `Base.metadata.create_all` at startup, starting the app will create the new table automatically (ensure `products.model.Product` uses `Base`).

10. Add tests (recommended)

- Add unit tests for service logic and endpoint tests using `httpx.AsyncClient` with `TestClient` or `pytest-asyncio`.
- Example test pattern:
  - Create a test DB or use a transactional fixture
  - Seed minimal data
  - Call endpoints and assert `status_code` and response body

11. Linting & formatting

- Use black/isort/ruff if project has them (not present in this repo). Run formatting before committing.

12. Commit & open PR

- Branch naming: `feature/<short-description>` or `fix/<short-description>`
- Include meaningful commit message and describe database changes, migrations (if any) in PR description.

## Notes on database migrations

- This project currently uses `Base.metadata.create_all` to create tables automatically. For production or controlled schema changes, add Alembic and create proper migration scripts.

## Example: Minimal file templates (copy & adapt)

- Router snippet (example):

  from fastapi import APIRouter, Depends
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.products.controller import ProductController
  from app.products.schemas import ProductCreateSchema, ProductUpdateSchema
  from app.database import get_db

  router = APIRouter(prefix="/products", tags=["Products"])

  @router.get("/", summary="List all products")
  async def list_products(db: AsyncSession = Depends(get_db)):
      return await ProductController(db).list_products()

(Use the categories module as the direct pattern to follow.)

## Helpful commands summary

- Install deps: `pip install -r requirements.txt`
- Start dev server: `uvicorn app.main:app --reload --port 8000`
- Docker compose up: `docker-compose up -d --build`
- Tail API logs: `docker-compose logs -f api`
- Health check: `curl http://localhost:8000/api/v1/health`

## Contacts

- Ask repository owner or the team for any missing conventions (testing strategy, code style, CI rules).

---

That's everything you need to be productive. Use the `categories` module as the canonical example when adding new features.
