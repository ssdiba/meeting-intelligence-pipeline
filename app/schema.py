from typing import Optional

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task: str
    owner: Optional[str] = None
    due_date: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractionResult(BaseModel):
    action_items: list[ActionItem]
