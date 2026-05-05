from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class PostSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)

class PostCreateSchema(PostSchema):
    pass

class PostUpdateSchema(PostSchema):
    title: str = Field(min_length=1, max_length=255, default=None)
    content: str = Field(min_length=1, default=None)
    author: str = Field(min_length=1, max_length=100, default=None)

class PostResponse(PostSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime