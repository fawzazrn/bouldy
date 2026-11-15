from datetime import date as Date
from app.models.enums import RouteKind
from app.models.enums import RouteStyle
from app.models.enums import RouteStatus

from pydantic import BaseModel, ConfigDict, Field


class RouteBase(BaseModel):
    gym_id: int
    route_name: str
    colour: str | None = None
    wall: str | None = None
    setter: str | None = None
    set_date: Date | None = None
    retired_date: Date | None = None


class RouteCreate(RouteBase):
    # Gyms that belong to a brand must use grade_id. `grade` free text is only
    # accepted for gyms without a brand (the original behaviour). A route with
    # only a route_kind (for example a wildcard) needs neither.
    grade: str | None = Field(default=None, max_length=10)
    grade_id: int | None = None
    route_kind: RouteKind | None = None
    styles: list[RouteStyle] = Field(default_factory=list)


class RouteUpdate(BaseModel):
    gym_id: int | None = None
    route_name: str | None = None
    grade: str | None = Field(default=None, max_length=10)
    grade_id: int | None = None
    route_kind: RouteKind | None = None
    colour: str | None = None
    wall: str | None = None
    setter: str | None = None
    set_date: Date | None = None
    retired_date: Date | None = None
    styles: list[RouteStyle] | None = None


class RouteResponse(RouteBase):
    id: int
    # Always present. For locked grades it mirrors the grade label.
    grade: str
    grade_id: int | None = None
    route_kind: RouteKind | None = None
    styles: list[RouteStyle]
    status: RouteStatus

    model_config = ConfigDict(from_attributes=True)
