import asyncio

from app.categories.schemas import CategoryCreateSchema
from app.celery_app import celery_app
from app.database import AsyncSessionLocal


@celery_app.task(name="categories.create_category", bind=True, max_retries=3)
def create_category_task(self, data: dict) -> dict:
    """
    Background task that creates a Category record in the database.
    Dispatched by the API when POST /categories is called.
    """
    async def _run():
        from app.categories.service import CategoryService

        async with AsyncSessionLocal() as db:
            service = CategoryService(db)
            schema = CategoryCreateSchema(**data)
            try:
                category = await service.create(schema)
                return {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "parent_id": category.parent_id,
                    "is_active": category.is_active,
                    "created_at": category.created_at.isoformat(),
                    "updated_at": category.updated_at.isoformat(),
                }
            except ValueError as exc:
                # Re-raise as Celery retryable failure
                raise self.retry(exc=exc, countdown=5)

    return asyncio.run(_run())
