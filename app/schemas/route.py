from datetime import date as Date
from app.models.enums import RouteStyle
from app.models.enums import RouteStatus

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RouteStyle


class RouteBase(BaseModel):
    gym_id: int
    route_name: str
    grade: str 
    colour: str | None = None
    wall: str | None = None
    setter: str | None = None
    set_date: Date | None = None
    retired_date: Date | None = None

class RouteCreate(RouteBase):
    styles: list[RouteStyle] = Field(default_factory=list)  


class RouteUpdate(BaseModel):
    gym_id: int | None = None
    route_name: str | None = None
    grade: str | None = None
    colour: str | None = None
    wall: str | None = None
    setter: str | None = None
    set_date: Date | None = None
    retired_date: Date | None = None
    styles: list[RouteStyle] | None = None


class RouteResponse(RouteBase):
    id: int
    styles: list[RouteStyle]
    status: RouteStatus

    model_config = ConfigDict(from_attributes=True)