from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TodoCreate(BaseModel):
    title: str
    category: str = "general"


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    done: bool
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}
