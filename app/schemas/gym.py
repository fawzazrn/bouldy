from pydantic import BaseModel, ConfigDict


class GymBase(BaseModel):
    name: str
    location: str


class GymCreate(GymBase):
    pass


class GymUpdate(BaseModel):
    name: str | None = None
    location: str | None = None


class GymResponse(GymBase):
    id: int

    model_config = ConfigDict(from_attributes=True)