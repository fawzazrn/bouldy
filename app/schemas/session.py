from datetime import date

from pydantic import BaseModel, ConfigDict


class SessionBase(BaseModel):
    user_id: int
    gym_id: int
    session_date: date
    duration_minutes: int
    notes: str | None = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    duration_minutes: int | None = None
    notes: str | None = None


class SessionResponse(SessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)