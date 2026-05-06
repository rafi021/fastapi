from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.controller import CategoryController
from app.categories.schemas import CategoryCreateSchema, CategoryUpdateSchema
from app.database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", summary="List all categories")
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
):
    return await CategoryController(db).list_categories(skip, limit)


@router.get("/{category_id}", summary="Get a category by ID")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    return await CategoryController(db).get_category(category_id)


@router.post("/", status_code=201, summary="Create a new category")
async def create_category(data: CategoryCreateSchema, db: AsyncSession = Depends(get_db)):
    return await CategoryController(db).create_category(data)


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
