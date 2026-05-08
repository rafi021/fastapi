from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.controller import CategoryController
from app.categories.schemas import CategoryCreateSchema, CategoryUpdateSchema
from app.categories.tasks import create_category_task
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/category-tree", summary="Get category tree")
async def get_category_tree(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    search: Optional[str] = Query(None, description="Search term"),
    db: AsyncSession = Depends(get_db)):
    return await CategoryController(db).get_category_tree(skip, limit, search)

@router.get("/", summary="List all categories")
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    search: Optional[str] = Query(None, description="Search term"),
    db: AsyncSession = Depends(get_db)):
    return await CategoryController(db).list_categories(skip, limit, search)


@router.get("/{category_id}", summary="Get a category by ID")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    return await CategoryController(db).get_category(category_id)


@router.post("/", status_code=202, summary="Create a new category (async via Celery)")
async def create_category(data: CategoryCreateSchema, db: AsyncSession = Depends(get_db)):
    """
    Dispatches a Celery background task to create the category via RabbitMQ.
    Returns 202 Accepted with the task ID immediately.
    Poll the task status at GET /api/v1/categories/tasks/{task_id}
    """
    task = create_category_task.delay(data.model_dump())
    return JSONResponse(
        status_code=202,
        content={
            "success": True,
            "message": "Category creation queued",
            "task_id": task.id,
        },
    )


@router.get("/tasks/{task_id}", summary="Get async task result")
async def get_task_result(task_id: str):
    """Check the status / result of a queued category creation task."""
    from celery.result import AsyncResult
    from app.celery_app import celery_app

    result: AsyncResult = celery_app.AsyncResult(task_id)
    response: dict = {"task_id": task_id, "status": result.status}
    if result.ready():
        if result.successful():
            response["data"] = result.result
        else:
            response["error"] = str(result.result)
    return response


@router.put("/{category_id}", summary="Update a category")
async def update_category(
    category_id: int,
    data: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    return await CategoryController(db).update_category(category_id, data)


@router.delete("/{category_id}", summary="Delete a category")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    return await CategoryController(db).delete_category(category_id)
