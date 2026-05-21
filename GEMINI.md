# GEMINI.md

## Project Overview
**E-Commerce API** is a high-performance RESTful service built with **FastAPI**, designed for scalability and maintainability. It implements a categories resource using an async-first approach and follows a strictly layered architecture.

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy 2.x](https://www.sqlalchemy.org/) (async) and `asyncpg`
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Background Tasks:** [Celery](https://docs.celeryq.dev/) with [RabbitMQ](https://www.rabbitmq.com/) (broker) and [Redis](https://redis.io/) (backend)
- **Monitoring:** [Flower](https://flower.readthedocs.io/)
- **Infrastructure:** [Docker](https://www.docker.com/), `docker-compose`, [Nginx](https://www.nginx.com/), [Kubernetes](https://kubernetes.io/)

## Architecture & Conventions
The project follows a **Router -> Controller -> Service -> Model** layered pattern to ensure separation of concerns.

### Directory Structure
- `app/`: Main application source code.
  - `categories/`: Domain module for category management.
    - `router.py`: FastAPI route definitions.
    - `controller.py`: HTTP coordination and response shaping.
    - `service.py`: Business logic and database operations.
    - `model.py`: SQLAlchemy database models.
    - `schemas.py`: Pydantic request/response schemas.
    - `tasks.py`: Background tasks (Celery).
  - `core/`: Shared utilities and base models (e.g., `APIResponse`).
  - `main.py`: Application entry point and lifespan management.
  - `database.py`: SQLAlchemy engine and session configuration.
  - `config.py`: Environment-based settings using Pydantic Settings.

### Standards
- **Async-First:** All database and I/O operations must use `async/await`.
- **Response Shape:** All endpoints (via controllers) should return the `APIResponse` wrapper: `{ "success": bool, "message": str, "data": any | null }`.
- **Validation:** Use Pydantic v2 for data validation and serialization. Use `model_config = ConfigDict(from_attributes=True)` in response schemas to support SQLAlchemy models.
- **Service Layer:** Business logic belongs in the service layer. Services should raise `ValueError` for domain-level conflicts, which controllers map to appropriate HTTP exceptions.

## Building and Running

### Local Development
1. **Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run App:**
   ```bash
   # Using FastAPI CLI (recommended)
   fastapi dev app.main:app --reload
   
   # Using Uvicorn directly
   uvicorn app.main:app --reload --port 8000
   ```
3. **Run Worker:**
   ```bash
   celery -A app.celery_app.celery_app worker --loglevel=info
   ```

### Docker (Full Stack)
The project includes a complete stack (API, DB, Redis, RabbitMQ, Nginx, Flower).
```bash
docker-compose up -d --build
```

### Health Check
Verify the API and database connectivity:
```bash
curl http://localhost:8000/api/v1/health
```

## Development Workflow
1. **New Features:** Follow the `categories` module pattern. Create a new package under `app/` with `model`, `schemas`, `service`, `controller`, and `router`.
2. **Migrations:** Currently uses `Base.metadata.create_all` during app lifespan for automatic table creation in dev.
3. **Documentation:** OpenAPI (Swagger) documentation is available at `/docs` when the app is running.
