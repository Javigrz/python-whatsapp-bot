from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional

class BaseModel(SQLModel):
    id: Optional[int] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
