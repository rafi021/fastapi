from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[int] = Field(None, gt=0)
    is_active: bool = True


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parent_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    is_active: bool
    # created_at: datetime
    # updated_at: datetime

class CategoryTreeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    is_active: bool
    children: List["ChildCategoryResponse"] = []

class ChildCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str