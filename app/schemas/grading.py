from pydantic import BaseModel, ConfigDict

from app.models.enums import RouteKind


class GradeResponse(BaseModel):
    id: int
    label: str
    order: int
    colour_hex: str | None = None
    v_range_label: str | None = None
    font_range_label: str | None = None
    description: str | None = None
    band: str | None = None

    model_config = ConfigDict(from_attributes=True)


class GradeScaleResponse(BaseModel):
    id: int
    name: str
    kind: str
    version: int
    grades: list[GradeResponse]

    model_config = ConfigDict(from_attributes=True)


class GymBrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    grade_scale_id: int
    allowed_route_kinds: list[RouteKind]

    model_config = ConfigDict(from_attributes=True)


class GymBrandDetailResponse(GymBrandResponse):
    grade_scale: GradeScaleResponse


class GymGradingResponse(BaseModel):
    """What a client needs to build a grade picker for one gym."""

    gym_id: int
    brand_id: int | None
    scale: GradeScaleResponse | None
    allowed_route_kinds: list[RouteKind]
    # True when the gym has a brand, so free-text grades are rejected.
    grade_required: bool
