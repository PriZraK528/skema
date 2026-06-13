from __future__ import annotations

from pydantic import BaseModel


class PatientBrief(BaseModel):
    id: int
    full_name: str
    phone: str

    model_config = {"from_attributes": True}
