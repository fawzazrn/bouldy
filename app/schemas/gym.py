from pydantic import BaseModel, ConfigDict


class GymBase(BaseModel):
    name: str
    location: str


class GymCreate(GymBase):
    brand_id: int | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    opening_hours: str | None = None


class GymUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    brand_id: int | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    opening_hours: str | None = None
    is_active: bool | None = None


class GymResponse(GymBase):
    id: int
    brand_id: int | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    opening_hours: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
