from typing import Optional, Sequence
from unittest import result

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.categories.model import Category
from app.categories.schemas import CategoryCreateSchema, CategoryUpdateSchema


class CategoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_categories(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Sequence[Category]:
        query = (
            select(Category)
            .where(Category.parent_id == None)  # Get only top-level parents for a tree
            .options(selectinload(Category.children))
        )
        if search:
            query = query.where(Category.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_all(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Sequence[Category]:
        query = (
            select(Category)
            .options(
                selectinload(Category.parent),  # Loads the parent
                selectinload(Category.children)  # Loads the list of children
            )
            .order_by(Category.id)
            .offset(skip)
            .limit(limit)
        )
        if search:
            query = query.where(Category.name.ilike(f"%{search}%"))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(
            select(Category)
            .options(
                selectinload(Category.parent),  # Loads the parent
                selectinload(Category.children)  # Loads the list of children
            )
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, data: CategoryCreateSchema) -> Category:
        if await self.get_by_name(data.name):
            raise ValueError(f"Category '{data.name}' already exists")

        if data.parent_id is not None and not await self.get_by_id(data.parent_id):
            raise ValueError(f"Parent category with id {data.parent_id} not found")

        category = Category(**data.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category_id: int, data: CategoryUpdateSchema) -> Optional[Category]:
        category = await self.get_by_id(category_id)
        if not category:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != category.name:
            if await self.get_by_name(update_data["name"]):
                raise ValueError(f"Category '{update_data['name']}' already exists")

        if update_data.get("parent_id") is not None:
            if update_data["parent_id"] == category_id:
                raise ValueError("A category cannot be its own parent")
            if not await self.get_by_id(update_data["parent_id"]):
                raise ValueError(f"Parent category with id {update_data['parent_id']} not found")

        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: int) -> bool:
        category = await self.get_by_id(category_id)
        if not category:
            return False

        await self.db.delete(category)
        await self.db.commit()
        return True
