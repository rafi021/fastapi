from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CategoryCreateSchema, CategoryResponse, CategoryUpdateSchema
from app.categories.service import CategoryService
from app.core.response import APIResponse


class CategoryController:
    def __init__(self, db: AsyncSession) -> None:
        self.service = CategoryService(db)

    async def list_categories(self, skip: int = 0, limit: int = 100) -> APIResponse:
        categories = await self.service.get_all(skip, limit)
        return APIResponse.ok(
            data=[CategoryResponse.model_validate(c) for c in categories],
            message="Categories retrieved successfully",
        )

    async def get_category(self, category_id: int) -> APIResponse:
        category = await self.service.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )
        return APIResponse.ok(
            data=CategoryResponse.model_validate(category),
            message="Category retrieved successfully",
        )

    async def create_category(self, data: CategoryCreateSchema) -> APIResponse:
        try:
            category = await self.service.create(data)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        return APIResponse.ok(
            data=CategoryResponse.model_validate(category),
            message="Category created successfully",
        )

    async def update_category(self, category_id: int, data: CategoryUpdateSchema) -> APIResponse:
        try:
            category = await self.service.update(category_id, data)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )
        return APIResponse.ok(
            data=CategoryResponse.model_validate(category),
            message="Category updated successfully",
        )

    async def delete_category(self, category_id: int) -> APIResponse:
        deleted = await self.service.delete(category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )
        return APIResponse.ok(message=f"Category {category_id} deleted successfully")
