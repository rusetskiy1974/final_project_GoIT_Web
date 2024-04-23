from typing import Optional, List
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.models.models import Tag
from src.schemas.user import UserReadSchema


class ImageReadSchema(BaseModel):
    id: int
    title: str
    image_path: str
    mime_type: str
    created_at: datetime
    updated_at: datetime
    count_tags: Optional[int] = 0
    owner: UserReadSchema

    model_config = ConfigDict(from_attributes=True)


class ImageCreateSchema(BaseModel):
    name: str
    size: int
    title: str
    image_path: str
    mime_type: str


