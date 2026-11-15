# app/models/enums.py
from enum import Enum

class RouteStyle(str, Enum):
    CRIMPS = "Crimps"
    SLOPERS = "Slopers"
    PINCHES = "Pinches"
    JUGS = "Jugs"
    POCKETS = "Pockets"

    DYNO = "Dyno"
    DEADPOINT = "Deadpoint"
    STATIC = "Static"
    COORDINATION = "Coordination"

    SLAB = "Slab"
    VERTICAL = "Vertical"
    OVERHANG = "Overhang"
    ROOF = "Roof"

    COMPRESSION = "Compression"
    BALANCE = "Balance"
    MANTLE = "Mantle"
    HEEL_HOOK = "Heel Hook"
    TOE_HOOK = "Toe Hook"
    GASTON = "Gaston"
    
class AttemptResult(str, Enum):
    FLASH = "flash"
    ZONE = "zone"
    SEND = "send"
    PROJECT = "project"
    
class RouteStatus(str, Enum):
    ACTIVE = "active"
    RETIRED = "retired"


class RouteKind(str, Enum):
    """Special route types. Not grades, and not the climber's own project."""

    WILDCARD = "wildcard"
    SIGNATURE_SEND = "signature_send"
    GYM_PROJECT = "gym_project"


# Short text copied into the legacy routes.grade column (max 10 characters)
# when a route has a kind but no fixed grade.
ROUTE_KIND_GRADE_TEXT = {
    RouteKind.WILDCARD: "Wildcard",
    RouteKind.SIGNATURE_SEND: "Signature",
    RouteKind.GYM_PROJECT: "Project",
}


class GradeScaleKind(str, Enum):
    NUMERIC = "numeric"
    COLOUR_TIER = "colour_tier"


class GradeBand(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"