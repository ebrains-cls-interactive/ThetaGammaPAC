from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_serializer, field_validator


class Job(BaseModel):
    id: str
    title: str
    execution: str
    status: str
    created_at: datetime
    service: Literal['Unicore', 'NSG', 'CLS-Service-Account']
    hpc: str
    downloaded: Literal['Downloading', 'Yes', 'No'] = 'No'

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime, _info) -> str:
        return v.isoformat()

    @field_validator("created_at")
    def validate_created_at(cls, v: datetime | str) -> datetime:
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

    def __str__(self) -> str:
        return f'{self.id} - {self.title} - {self.execution}'
